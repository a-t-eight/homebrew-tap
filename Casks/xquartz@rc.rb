cask "xquartz@rc" do
  version "2.8.6_rc2"
  sha256 "ca85d005c85f867ff4b5fb446cd6149ff70bc0f178fd7855ee880cd39b2243cd"

  url "https://github.com/XQuartz/XQuartz/releases/download/XQuartz-#{version}/XQuartz-#{version}.pkg",
      verified: "github.com/XQuartz/XQuartz/"
  name "XQuartz"
  desc "Pre-release version of the X.Org X Window System"
  homepage "https://www.xquartz.org/"

  livecheck do
    url "https://www.xquartz.org/releases/sparkle-r1/rc.xml"
    strategy :sparkle do |items|
      items.filter_map do |item|
        version = item.short_version&.delete_prefix("XQuartz-")
        next if version.nil?

        version if version.match?(/\A\d+(?:\.\d+)+_rc\d+\z/i)
      end
    end
  end

  auto_updates true
  depends_on :macos

  pkg "XQuartz-#{version}.pkg"

  uninstall launchctl: "org.xquartz.privileged_startx",
            pkgutil:   "org.xquartz.X11"

  zap trash: [
        "~/.Xauthority",
        "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/org.xquartz.x11.sfl*",
        "~/Library/Application Support/XQuartz",
        "~/Library/Caches/org.xquartz.X11",
        "~/Library/Cookies/org.xquartz.X11.binarycookies",
        "~/Library/HTTPStorages/org.xquartz.X11",
        "~/Library/Logs/X11/org.xquartz.log",
        "~/Library/Logs/X11/org.xquartz.log.old",
        "~/Library/Preferences/org.macosforge.xquartz.X11.plist",
        "~/Library/Preferences/org.xquartz.X11.plist",
        "~/Library/Saved Application State/org.xquartz.X11.savedState",
        "~/Library/WebKit/org.xquartz.X11",
      ],
      rmdir: [
        "~/.fonts",
        "~/Library/Logs/X11",
      ]
end
