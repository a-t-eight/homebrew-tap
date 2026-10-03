import copy
import datetime as dt
import hashlib
import importlib.util
import re
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("updater", ROOT / "scripts/update_displaycal.py")
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


def release(version="3.9.20"):
    return {
        "tag_name": version,
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": f"DisplayCAL-{version}-macOS-{arch}.dmg",
                "browser_download_url": f"https://github.com/eoyilmaz/displaycal-py3/releases/download/{version}/DisplayCAL-{version}-macOS-{arch}.dmg",
                "digest": "sha256:" + hashlib.sha256(arch.encode()).hexdigest(),
            }
            for arch in ("arm64", "x86_64")
        ],
    }


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cask = self.root / "displaycal-py3.rb"
        self.original = re.sub(r'^  version "[^"]+"$', '  version "3.9.19"',
                               (ROOT / "Casks/displaycal-py3.rb").read_text(), flags=re.MULTILINE)
        self.cask.write_text(self.original)

    def download(self, asset, destination):
        arch = "arm64" if "arm64" in asset["name"] else "x86_64"
        destination.write_bytes(arch.encode())

    def update(self, data, download=None):
        return updater.update(self.cask, data, self.root, download or self.download)

    def test_fortnightly_cadence_survives_year_boundary(self):
        for day, expected in (("2026-10-05", True), ("2026-10-12", False),
                              ("2026-10-19", True), ("2026-12-28", True),
                              ("2027-01-04", False), ("2027-01-11", True),
                              ("2026-10-06", False), ("2026-09-21", False)):
            with self.subTest(day=day):
                self.assertEqual(updater.is_due(dt.date.fromisoformat(day)), expected)

    def test_new_release_updates_version_and_both_hashes(self):
        result = self.update(release())
        self.assertEqual(result, {"updated": True, "version": "3.9.20"})
        text = self.cask.read_text()
        self.assertIn('version "3.9.20"', text)
        for arch in ("arm64", "x86_64"):
            self.assertIn(hashlib.sha256(arch.encode()).hexdigest(), text)
        self.assertIn('suite "DisplayCAL"', text)
        self.assertEqual(self.update(release())["updated"], False)

    def test_current_or_older_release_does_not_download_or_change_file(self):
        def unexpected_download(*args):
            self.fail("unchanged releases must not download")
        for version in ("3.9.19", "3.9.9"):
            self.assertFalse(self.update(release(version), unexpected_download)["updated"])
            self.assertEqual(self.cask.read_text(), self.original)

    def test_verify_current_checks_assets_without_modifying_cask(self):
        self.update(release())
        before = self.cask.read_text()
        result = updater.update(self.cask, release(), self.root, self.download, verify_current=True)
        self.assertFalse(result["updated"])
        self.assertEqual(self.cask.read_text(), before)

    def test_verify_current_rejects_replaced_release_asset(self):
        self.update(release())
        before = self.cask.read_text()
        data = release()
        data["assets"][0]["digest"] = "sha256:" + hashlib.sha256(b"replacement").hexdigest()
        def replaced(asset, destination):
            destination.write_bytes(b"replacement" if "arm64" in asset["name"] else b"x86_64")
        with self.assertRaises(ValueError):
            updater.update(self.cask, data, self.root, replaced, verify_current=True)
        self.assertEqual(self.cask.read_text(), before)

    def test_missing_or_duplicate_assets_leave_cask_unchanged(self):
        data = release()
        for assets in (data["assets"][:1], data["assets"] + data["assets"][:1]):
            broken = copy.deepcopy(data)
            broken["assets"] = assets
            with self.assertRaises(ValueError):
                self.update(broken)
            self.assertEqual(self.cask.read_text(), self.original)

    def test_bad_checksum_leaves_cask_unchanged(self):
        data = release()
        data["assets"][1]["digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            self.update(data)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_missing_digest_is_rejected(self):
        data = release()
        data["assets"][0]["digest"] = None
        with self.assertRaises(ValueError):
            self.update(data)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_unexpected_asset_url_is_rejected(self):
        data = release()
        data["assets"][0]["browser_download_url"] = "https://example.com/asset.dmg"
        with self.assertRaises(ValueError):
            self.update(data)

    def test_unstable_or_malformed_tags_are_rejected(self):
        for key, value in (("draft", True), ("prerelease", True),
                           ("tag_name", "3.9.20\nupdated=true")):
            data = release()
            data[key] = value
            with self.assertRaises(ValueError):
                self.update(data)

    def test_download_failure_leaves_cask_unchanged(self):
        def failed_download(*args):
            raise OSError("download failed")
        with self.assertRaises(OSError):
            self.update(release(), failed_download)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_unexpected_cask_layout_is_not_partially_updated(self):
        self.cask.write_text(self.original.replace("sha256 arm:", "sha256:"))
        before = self.cask.read_text()
        with self.assertRaises(ValueError):
            self.update(release())
        self.assertEqual(self.cask.read_text(), before)


if __name__ == "__main__":
    unittest.main()
