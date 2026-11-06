// Gris (NeXTSTEP) for Firefox. Symlinked into the profile by ~/.config/dotfiles/firefox/install.sh
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);  // load chrome/userChrome.css
user_pref("extensions.activeThemeID", "default-theme@mozilla.org");  // light base that follows GTK; userChrome.css repaints it
user_pref("browser.theme.toolbar-theme", 1);
user_pref("browser.theme.content-theme", 1);
user_pref("browser.tabs.inTitlebar", 1);  // tabs are the black title bar, with the GTK miniaturize (left) and close (right) buttons
user_pref("ui.key.menuAccessKeyFocuses", false);
user_pref("widget.gtk.overlay-scrollbars.enabled", false);  // NeXT scrollers: always there, dark trough (userContent.css)
user_pref("widget.non-native-theme.scrollbar.style", 4);  // square knob with arrow buttons
// Undo the vertical tabs morado sets (user.js prefs stay in prefs.js after switching theme)
user_pref("sidebar.verticalTabs", false);
user_pref("sidebar.position_start", true);
