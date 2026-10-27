// Rojo (constructivism) for Firefox. Symlinked into the profile by ~/.config/dotfiles/firefox/install.sh
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);  // load chrome/userChrome.css
user_pref("extensions.activeThemeID", "firefox-compact-light@mozilla.org");
user_pref("browser.theme.toolbar-theme", 1);
user_pref("browser.theme.content-theme", 1);
user_pref("browser.tabs.inTitlebar", 1);
user_pref("ui.key.menuAccessKeyFocuses", false);
// Undo the scrollbars azul sets (user.js prefs stay in prefs.js after switching theme)
user_pref("widget.gtk.overlay-scrollbars.enabled", true);
user_pref("widget.non-native-theme.scrollbar.style", 0);
