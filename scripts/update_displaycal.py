#!/usr/bin/env python3
"""Prepare a verified DisplayCAL cask update; publishing is handled by Actions."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/eoyilmaz/displaycal-py3"
ANCHOR = dt.date(2026, 10, 5)


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


def update(cask, release, download_dir, fetch=download, verify_current=False):
    original = cask.read_text()
    versions = re.findall(r'^  version "([^"]+)"$', original, re.MULTILINE)
    if len(versions) != 1:
        raise ValueError("Expected exactly one cask version")
    current = version_tuple(versions[0])
    version = release["tag_name"]
    latest = version_tuple(version)
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Refusing a draft or prerelease")
    if latest < current or (latest == current and not verify_current):
        return {"updated": False, "version": versions[0]}

    assets = {}
    for arch in ("arm64", "x86_64"):
        name = f"DisplayCAL-{version}-macOS-{arch}.dmg"
        matches = [a for a in release["assets"] if a["name"] == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one asset: {name}")
        asset = matches[0]
        if asset["browser_download_url"] != f"{UPSTREAM}/releases/download/{version}/{name}":
            raise ValueError(f"Unexpected download URL for {name}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", asset.get("digest") or ""):
            raise ValueError(f"Missing SHA-256 release digest for {name}")
        assets[arch] = asset

    download_dir.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for arch, asset in assets.items():
        destination = download_dir / asset["name"]
        fetch(asset, destination)
        with destination.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        if "sha256:" + digest != asset["digest"]:
            raise ValueError(f"Checksum mismatch for {asset['name']}")
        hashes[arch] = digest

    updated = original
    replacements = (
        (r'^  version "[^"]+"$', f'  version "{version}"'),
        (r'^  sha256 arm: +"[0-9a-f]{64}",$', f'  sha256 arm:   "{hashes["arm64"]}",'),
        (r'^         intel: "[0-9a-f]{64}"$', f'         intel: "{hashes["x86_64"]}"'),
    )
    for pattern, replacement in replacements:
        updated, count = re.subn(pattern, replacement, updated, flags=re.MULTILINE)
        if count != 1:
            raise ValueError("Cask layout changed; manual update required")
    if latest == current and updated != original:
        raise ValueError("Published asset hashes changed without a version change")
    if updated != original:
        temporary = cask.with_suffix(".rb.tmp")
        temporary.write_text(updated)
        temporary.replace(cask)

    (download_dir / "release.json").write_text(json.dumps({
        "version": version, "sha256": hashes,
    }, indent=2) + "\n")
    return {"updated": updated != original, "version": version}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--due", action="store_true", help="Print cadence eligibility without network access")
    parser.add_argument("--verify-current", action="store_true", help="Also download and verify the current version")
    parser.add_argument("--download-dir", type=Path, default=ROOT / "work/displaycal")
    args = parser.parse_args()
    if args.due:
        print(str(is_due(dt.datetime.now(dt.timezone.utc).date())).lower())
        return
    endpoint = "repos/eoyilmaz/displaycal-py3/releases/latest"
    if args.verify_current:
        text = (ROOT / "Casks/displaycal-py3.rb").read_text()
        version = re.search(r'^  version "([^"]+)"$', text, re.MULTILINE).group(1)
        version_tuple(version)
        endpoint = f"repos/eoyilmaz/displaycal-py3/releases/tags/{version}"
    release = json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))
    result = update(ROOT / "Casks/displaycal-py3.rb", release, args.download_dir,
                    verify_current=args.verify_current)
    print(json.dumps(result))
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as destination:
            for key, value in result.items():
                destination.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")


if __name__ == "__main__":
    main()
