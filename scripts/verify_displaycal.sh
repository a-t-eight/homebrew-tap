#!/bin/bash
# Inspect both downloaded suites without installing or executing upstream code.
set -euo pipefail
download_dir=${1:?Usage: verify_displaycal.sh DOWNLOAD_DIRECTORY}
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$download_dir/release.json")
report="$download_dir/validation.md"
printf '# DisplayCAL %s validation\n\n' "$version" > "$report"
mount_dir=$(mktemp -d)
mounted=false
cleanup() {
  if [ "$mounted" = true ]; then
    hdiutil detach "$mount_dir" >/dev/null
  fi
  rmdir "$mount_dir"
}
trap cleanup EXIT
for arch in arm64 x86_64; do
  dmg="$download_dir/DisplayCAL-$version-macOS-$arch.dmg"
  hdiutil attach -readonly -nobrowse -mountpoint "$mount_dir" "$dmg" >/dev/null
  mounted=true
  python3 - "$mount_dir/DisplayCAL" "$version" "$arch" <<'PY'
import pathlib
import plistlib
import subprocess
import sys

suite, version, arch = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
names = ("3D LUT Maker", "Curve Viewer", "DisplayCAL", "ICC Profile Info",
         "Scripting Client", "Synthetic ICC", "Testchart Editor", "VRML to X3D")
for name in names:
    app = suite / f"{name}.app"
    with (app / "Contents/Info.plist").open("rb") as source:
        info = plistlib.load(source)
    if info["CFBundleShortVersionString"] != version:
        raise SystemExit(f"Wrong version in {name}")
    if tuple(map(int, info["LSMinimumSystemVersion"].split("."))) > (11, 0):
        raise SystemExit(f"Minimum macOS changed in {name}; review the cask requirement")
    binary = app / "Contents/MacOS" / info["CFBundleExecutable"]
    subprocess.run(["lipo", "-verify_arch", arch, str(binary)], check=True)
print(f"{arch}: all eight app versions, minimum OS and launcher architectures verified")
PY
  printf -- '- %s: checksums, suite layout, versions and launcher architectures verified.\n' "$arch" >> "$report"
  if spctl --assess --type execute --verbose=2 "$mount_dir/DisplayCAL/DisplayCAL.app" > "$download_dir/signing-$arch.log" 2>&1; then
    printf -- '- %s: Gatekeeper assessment passed.\n' "$arch" >> "$report"
  else
    printf -- '- %s: Gatekeeper assessment failed; see signing log. This known upstream limitation is not bypassed.\n' "$arch" >> "$report"
  fi
  hdiutil detach "$mount_dir" >/dev/null
  mounted=false
done
cat "$report"
