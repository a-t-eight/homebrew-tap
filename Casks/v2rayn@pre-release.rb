cask "v2rayn@pre-release" do
  arch arm: "arm64", intel: "64"

  version "7.24.3"
  sha256 arm:   "aa47cb2aef9e06f5250fb6a8f76f7a4464d425dca59cd4a53181d5f19bdd00b7",
         intel: "aa4aba6c141b174057976d1b03d959b97a2e82d4748b461391e6b9ef1ebe3c73"

  url "https://github.com/2dust/v2rayN/releases/download/#{version}/v2rayN-macos-#{arch}.dmg"
  name "v2rayN Pre-release"
  desc "Pre-release GUI client for Xray, sing-box, and other proxy cores"
  homepage "https://github.com/2dust/v2rayN"

  livecheck do
    url "https://github.com/2dust/v2rayN"
    regex(/^v?(\d+(?:\.\d+)+)$/i)
    strategy :github_releases do |json, regex|
      json.filter_map do |release|
        next if release["draft"] || !release["prerelease"]

        match = release["tag_name"]&.match(regex)
        next if match.blank?

        match[1]
      end
    end
  end

  auto_updates true
  conflicts_with cask: "v2rayn"
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

    This cask follows releases explicitly marked as pre-release on GitHub.
    It conflicts with v2rayn because both casks install the same application
    bundle and use the same configuration directory.

    Back up ~/Library/Application Support/v2rayN before switching channels.
  EOS
end
