import copy
import datetime as dt
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "updater", Path(__file__).resolve().parents[1] / "scripts/update_idevice_pair.py"
)
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.cask = self.root / "idevice-pair.rb"
        self.original = 'cask "idevice-pair" do\n  version "1.1.0"\n  sha256 "' + "0" * 64 + '"\nend\n'
        self.cask.write_text(self.original)
        self.payload = b"test release payload"
        self.asset = {
            "name": "idevice_pair--macos-universal.dmg",
            "browser_download_url": updater.UPSTREAM + "/releases/download/v1.2.0/idevice_pair--macos-universal.dmg",
            "digest": "sha256:" + hashlib.sha256(self.payload).hexdigest(),
        }
        self.release = {"tag_name": "v1.2.0", "draft": False, "prerelease": False, "assets": [self.asset]}
        self.validated = []

    def update(self, release=None, payload=None, verify_current=False, validator=None):
        return updater.update(
            self.cask, release or self.release, self.root / "downloads",
            fetch=lambda asset, path: path.write_bytes(self.payload if payload is None else payload),
            validate=validator or (lambda path, version: self.validated.append(version)),
            verify_current=verify_current,
        )

    def test_updates_only_version_and_checksum_after_validation(self):
        result = self.update()
        expected = self.original.replace('"1.1.0"', '"1.2.0"').replace("0" * 64, self.asset["digest"][7:])
        self.assertEqual(self.cask.read_text(), expected)
        self.assertEqual(self.validated, ["1.2.0"])
        self.assertEqual(result, {"updated": True, "version": "1.2.0"})

    def test_current_or_older_version_is_noop(self):
        for tag in ("v1.1.0", "v1.0.0"):
            release = dict(self.release, tag_name=tag, assets=[])
            self.assertFalse(self.update(release)["updated"])
        self.assertEqual(self.cask.read_text(), self.original)
        self.assertEqual(self.validated, [])

    def test_rejects_untrusted_or_incomplete_release_without_editing(self):
        for field, value in (("draft", True), ("prerelease", True), ("tag_name", "v1.2.0-rc1"),
                             ("tag_name", "v1.2.0\n"), ("assets", []), ("assets", [self.asset, self.asset])):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.update(dict(self.release, **{field: value}))
            self.assertEqual(self.cask.read_text(), self.original)

    def test_rejects_unexpected_url_or_digest_without_download(self):
        for field, value in (("browser_download_url", "https://example.com/app.dmg"), ("digest", None)):
            release = copy.deepcopy(self.release)
            release["assets"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.update(release)
            self.assertFalse((self.root / "downloads").exists())

    def test_checksum_failure_preserves_cask(self):
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            self.update(payload=b"corrupted")
        self.assertEqual(self.cask.read_text(), self.original)
        self.assertEqual(self.validated, [])

    def test_bundle_validation_failure_preserves_cask(self):
        def reject(path, version):
            raise ValueError("Invalid app bundle")
        with self.assertRaisesRegex(ValueError, "Invalid app bundle"):
            self.update(validator=reject)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_refuses_same_version_replaced_asset(self):
        release = copy.deepcopy(self.release)
        release["tag_name"] = "v1.1.0"
        release["assets"][0]["browser_download_url"] = self.asset["browser_download_url"].replace("v1.2.0", "v1.1.0")
        with self.assertRaisesRegex(ValueError, "hash changed"):
            self.update(release, verify_current=True)
        self.assertEqual(self.cask.read_text(), self.original)

    def test_rejects_ambiguous_cask_layout(self):
        self.cask.write_text(self.original.replace('  sha256 ', '  # sha256 '))
        with self.assertRaisesRegex(ValueError, "Cask layout changed"):
            self.update()

    def test_fortnightly_cadence_across_year_boundary(self):
        for days in (-14, -1, 1, 7, 13, 15):
            self.assertFalse(updater.is_due(updater.ANCHOR + dt.timedelta(days=days)))
        for days in (0, 14, 28, 84, 364):
            self.assertTrue(updater.is_due(updater.ANCHOR + dt.timedelta(days=days)))


if __name__ == "__main__":
    unittest.main()
