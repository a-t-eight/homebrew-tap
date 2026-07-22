cask "chatgpt-classic@1.2026.119" do
  version "1.2026.119,1780053722"
  sha256 "d91350eca4bf05fd5ba091e90b9a9635d16c59ff8da0e5655ea6551147fb2a1d"

  url "https://persistent.oaistatic.com/sidekick/public/ChatGPT_Desktop_public_#{version.csv.first}_#{version.csv.second}.dmg",
      verified: "persistent.oaistatic.com/sidekick/public/"
  name "ChatGPT Classic"
  desc "OpenAI's previous ChatGPT desktop app pinned before known Classic regressions"
  homepage "https://chatgpt.com/"

  livecheck do
    skip "Pinned to the last known good ChatGPT Classic build before model-selection regressions"
  end

  conflicts_with cask: [
    "chatgpt-classic",
    "chatgpt-classic@1.2026.160",
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
    This cask pins ChatGPT Classic before known model-selection regressions.
    If the app prompts for an in-app update, accepting it may move it off this pinned version.
  EOS
end
