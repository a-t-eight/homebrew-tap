cask "lm-studio-bionic" do
  version "1.0.3,3"
  sha256 "d72b62249616bdc98d0b8f2e8db3d0fa667453c9b289d09b1434f2e396d41c62"

  url "https://bionic-installers.lmstudio.ai/darwin/arm64/#{version.tr(",", "-")}/Bionic-#{version.tr(",", "-")}-arm64.dmg"
  name "LM Studio Bionic"
  desc "AI agent for working with open models"
  homepage "https://lmstudio.ai/"

  livecheck do
    url "https://lmstudio.ai/download/bionic/latest/darwin/arm64"
    regex(%r{/arm64/(\d+(?:\.\d+)+)-(\d+)/Bionic-}i)
    strategy :header_match do |headers, regex|
      location = headers["location"]
      location = location.last if location.is_a?(Array)
      match = location&.match(regex)
      next if match.blank?

      "#{match[1]},#{match[2]}"
    end
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :monterey

  app "Bionic.app"

  uninstall quit: "ai.elementlabs.bionic"

  zap trash: [
    "~/Library/Application Support/Bionic",
    "~/Library/Caches/ai.elementlabs.bionic",
    "~/Library/Caches/ai.elementlabs.bionic.ShipIt",
    "~/Library/HTTPStorages/ai.elementlabs.bionic",
    "~/Library/Logs/Bionic",
    "~/Library/Preferences/ai.elementlabs.bionic.plist",
    "~/Library/Saved Application State/ai.elementlabs.bionic.savedState",
  ]
end
