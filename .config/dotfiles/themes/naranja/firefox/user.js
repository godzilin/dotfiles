// Nostromo for Firefox. Symlinked into the profile by ~/.config/dotfiles/firefox/install.sh
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);  // load chrome/userChrome.css
user_pref("extensions.activeThemeID", "firefox-compact-dark@mozilla.org");  // dark base; userChrome.css repaints it
user_pref("browser.theme.toolbar-theme", 0);
user_pref("browser.theme.content-theme", 0);
user_pref("ui.key.menuAccessKeyFocuses", false);
