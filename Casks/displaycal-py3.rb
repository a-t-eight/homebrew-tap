cask "displaycal-py3" do
  arch arm: "arm64", intel: "x86_64"

  version "3.9.19"
  sha256 arm:   "e2a9e075e9ed30aafe6612d11578d217e3e80489fd6d50459406c112a3d7db19",
         intel: "dc0ca1107c5cd8c3dc67562445a642057716550a582430f17609ce2f80d2d50b"

  url "https://github.com/eoyilmaz/displaycal-py3/releases/download/#{version}/DisplayCAL-#{version}-macOS-#{arch}.dmg"
  name "DisplayCAL"
  desc "Display calibration and characterization powered by ArgyllCMS"
  homepage "https://github.com/eoyilmaz/displaycal-py3"

  livecheck do
    url :url
    strategy :github_latest
  end

  conflicts_with cask: "displaycal"
  depends_on formula: "argyll-cms"
  depends_on :macos

  suite "DisplayCAL"

  caveats <<~EOS
    The upstream macOS release is ad-hoc signed and may be blocked by Gatekeeper.
    This cask preserves quarantine and does not modify the upstream signatures.

    Launch DisplayCAL/DisplayCAL.app from your Applications directory.
    If ArgyllCMS is not detected, use "Locate ArgyllCMS executables" and select:
      #{HOMEBREW_PREFIX}/bin
  EOS
end
