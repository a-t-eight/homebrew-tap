cask "chatgpt-classic@1.2026.160" do
  version "1.2026.160,1781312926"
  sha256 "37e043abd3ffa592c4c2ba9ce8494bc3fa3b157ae4e6f7872a792ffd089edf07"

  url "https://persistent.oaistatic.com/sidekick/public/ChatGPT_Desktop_public_#{version.csv.first}_#{version.csv.second}.dmg",
      verified: "persistent.oaistatic.com/sidekick/public/"
  name "ChatGPT Classic"
  desc "OpenAI's previous ChatGPT desktop app pinned to build 1.2026.160"
  homepage "https://chatgpt.com/"

  livecheck do
    skip "Pinned ChatGPT Classic test build"
  end

  conflicts_with cask: [
    "chatgpt",
    "chatgpt-classic",
    "chatgpt-classic@1.2026.119",
  ]
  depends_on macos: :sonoma
  depends_on arch: :arm64

  app "ChatGPT.app"

  uninstall quit: "com.openai.chat"

  zap trash: [
    "~/Library/Application Scripts/com.openai.chat.Widgets",
    "~/Library/Application Scripts/group.com.openai.chat",
    "~/Library/Application Support/ChatGPT",
    "~/Library/Application Support/com.openai.chat",
    "~/Library/Caches/com.openai.chat",
    "~/Library/Containers/com.openai.chat.Widgets",
    "~/Library/Group Containers/group.com.openai.chat",
    "~/Library/HTTPStorages/ChatGPTHelper.binarycookies",
    "~/Library/HTTPStorages/com.openai.chat",
    "~/Library/HTTPStorages/com.openai.chat.binarycookies",
    "~/Library/Preferences/com.openai.chat.*.plist",
    "~/Library/Preferences/com.openai.chat.plist",
    "~/Library/Saved Application State/com.openai.chat.savedState",
    "~/Library/WebKit/com.openai.chat",
  ]

  caveats <<~EOS
    This cask pins ChatGPT Classic to 1.2026.160 for comparison testing.
    A regression was reported in 1.2026.153, so keep 1.2026.119 available as the conservative fallback.
    If the app prompts for an in-app update, accepting it may move it off this pinned version.
  EOS
end
