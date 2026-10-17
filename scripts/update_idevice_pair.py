#!/usr/bin/env python3
"""Validate a stable upstream DMG and prepare a checksum-pinned cask update."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/jkcoxson/idevice_pair"
ANCHOR = dt.date(2026, 10, 19)
ASSET_NAME = "idevice_pair--macos-universal.dmg"


def is_due(today):
    days = (today - ANCHOR).days
    return days >= 0 and days % 14 == 0


def version_tuple(version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected a stable three-component numeric version")
    return tuple(map(int, version.split(".")))


def download(asset, destination):
    subprocess.run([
        "curl", "--fail", "--location", "--retry", "3", "--silent", "--show-error",
        "--proto", "=https", "--proto-redir", "=https", "--max-time", "600",
        "--output", str(destination), asset["browser_download_url"],
    ], check=True)


def validate_bundle(dmg, version):
    """Inspect without launching the app or accessing any pairing records."""
    with tempfile.TemporaryDirectory(prefix="idevice-pair-") as directory:
        mount = Path(directory) / "mount"
        mount.mkdir()
        subprocess.run([
            "hdiutil", "attach", "-readonly", "-nobrowse", "-mountpoint", str(mount), str(dmg),
        ], check=True)
        try:
            app = mount / "idevice_pair.app"
            with (app / "Contents/Info.plist").open("rb") as source:
                info = plistlib.load(source)
            expected = {
                "CFBundleIdentifier": "com.jkcoxson.idevice_pair",
                "CFBundleShortVersionString": version,
                "CFBundleExecutable": "idevice_pair",
                "CFBundlePackageType": "APPL",
            }
            for key, value in expected.items():
                if info.get(key) != value:
                    raise ValueError(f"Unexpected {key}: {info.get(key)!r}")
            binary = app / "Contents/MacOS/idevice_pair"
            if not os.access(binary, os.X_OK):
                raise ValueError("App executable is not executable")
            for arch in ("arm64", "x86_64"):
                subprocess.run(["lipo", str(binary), "-verify_arch", arch], check=True)
            subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)
            subprocess.run(["spctl", "--assess", "--type", "execute", "--verbose=2", str(app)], check=True)
            print(f"Validated {version}: bundle identity, universal binary, code signature and Gatekeeper", flush=True)
        finally:
            subprocess.run(["hdiutil", "detach", str(mount)], check=True)


def update(cask, release, download_dir, fetch=download, validate=validate_bundle, verify_current=False):
    original = cask.read_text()
    versions = re.findall(r'^  version "([^"]+)"$', original, re.MULTILINE)
    if len(versions) != 1:
        raise ValueError("Expected exactly one cask version")
    current = version_tuple(versions[0])
    tag = release["tag_name"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Expected a stable v-prefixed release tag")
    version = tag[1:]
    latest = version_tuple(version)
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Refusing a draft or prerelease")
    if latest < current or (latest == current and not verify_current):
        return {"updated": False, "version": versions[0]}

    matches = [asset for asset in release["assets"] if asset["name"] == ASSET_NAME]
    if len(matches) != 1:
        raise ValueError("Expected exactly one universal macOS DMG")
    asset = matches[0]
    if asset["browser_download_url"] != f"{UPSTREAM}/releases/download/{tag}/{ASSET_NAME}":
        raise ValueError("Unexpected download URL")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", asset.get("digest") or ""):
        raise ValueError("Missing SHA-256 release digest")

    download_dir.mkdir(parents=True, exist_ok=True)
    destination = download_dir / ASSET_NAME
    fetch(asset, destination)
    with destination.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if "sha256:" + digest != asset["digest"]:
        raise ValueError("Checksum mismatch")

    updated = original
    for pattern, replacement in (
        (r'^  version "[^"]+"$', f'  version "{version}"'),
        (r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{digest}"'),
    ):
        updated, count = re.subn(pattern, replacement, updated, flags=re.MULTILINE)
        if count != 1:
            raise ValueError("Cask layout changed; manual update required")
    if latest == current and updated != original:
        raise ValueError("Published asset hash changed without a version change")

    validate(destination, version)
    if updated != original:
        temporary = cask.with_suffix(".rb.tmp")
        temporary.write_text(updated)
        temporary.replace(cask)
    (download_dir / "validation.json").write_text(json.dumps({
        "version": version, "sha256": digest, "release": f"{UPSTREAM}/releases/tag/{tag}",
        "checks": ["bundle identity", "arm64", "x86_64", "codesign", "Gatekeeper"],
    }, indent=2) + "\n")
    return {"updated": updated != original, "version": version}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--due", action="store_true")
    parser.add_argument("--verify-current", action="store_true", help="Validate the pinned release, even if unchanged")
    args = parser.parse_args()
    if args.due:
        print(str(is_due(dt.datetime.now(dt.timezone.utc).date())).lower())
        return
    cask = ROOT / "Casks/idevice-pair.rb"
    endpoint = "repos/jkcoxson/idevice_pair/releases/latest"
    if args.verify_current:
        version = re.search(r'^  version "([^"]+)"$', cask.read_text(), re.MULTILINE).group(1)
        version_tuple(version)
        endpoint = f"repos/jkcoxson/idevice_pair/releases/tags/v{version}"
    release = json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))
    result = update(cask, release, ROOT / "work/idevice-pair", verify_current=args.verify_current)
    print(json.dumps(result))
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as destination:
            for key, value in result.items():
                destination.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")


if __name__ == "__main__":
    main()
