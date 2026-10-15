// Azul (Windows 98) for Firefox. Symlinked into the profile by ~/.config/dotfiles/firefox/install.sh
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);  // load chrome/userChrome.css
user_pref("extensions.activeThemeID", "default-theme@mozilla.org");  // follows the GTK theme (Chicago95)
user_pref("browser.theme.toolbar-theme", 1);
user_pref("browser.theme.content-theme", 1);
user_pref("browser.tabs.inTitlebar", 1);
user_pref("ui.key.menuAccessKeyFocuses", false);
user_pref("widget.gtk.overlay-scrollbars.enabled", false);  // real Win95 scrollbars
