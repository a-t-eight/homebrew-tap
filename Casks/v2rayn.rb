cask "v2rayn" do
  arch arm: "arm64", intel: "64"

  version "7.23.4"
  sha256 arm:   "6cfbd8dbfd7be87b4f56245fef1483fc6fd6cb43a1a693505c8ac6087d838533",
         intel: "5cc04792bbe8a43b28af11f900765b0a37b11c9b93116a02f06dde5abae12ed9"

  url "https://github.com/2dust/v2rayN/releases/download/#{version}/v2rayN-macos-#{arch}.dmg"
  name "v2rayN"
  desc "GUI client for Xray, sing-box, and other proxy cores"
  homepage "https://github.com/2dust/v2rayN"

  livecheck do
    url "https://github.com/2dust/v2rayN"
    strategy :github_latest
  end

  auto_updates true
  conflicts_with cask: "v2rayn@pre-release"
  depends_on macos: :ventura

  app "v2rayN.app"

  uninstall launchctl: "v2rayN-LaunchAgent",
            quit:      "2dust.v2rayN",
            script:    {
              executable:   "/usr/bin/pkill",
              args:         [
                "-TERM",
                "-f",
                "^#{Regexp.escape(Dir.home)}/Library/Application Support/v2rayN/bin/",
              ],
              must_succeed: false,
            },
            trash:     "~/Library/LaunchAgents/v2rayN-LaunchAgent.plist"

  zap trash: [
    "~/Library/Application Support/v2rayN",
    "~/Library/Preferences/2dust.v2rayN.plist",
  ]

  caveats <<~EOS
    The upstream macOS application is only ad-hoc signed and does not pass
    Apple's Gatekeeper verification. It is not Developer ID signed or notarised.

    Verify the downloaded release and its upstream GPG signature before
    applying any Gatekeeper workaround.

    This cask follows stable GitHub releases. It conflicts with
    v2rayn@pre-release because both casks install the same application bundle.
  EOS
end
