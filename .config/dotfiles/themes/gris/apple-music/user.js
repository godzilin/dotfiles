// Perfil de Firefox solo para Apple Music (lanzado por ~/.local/share/applications/apple-music.desktop)
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
user_pref("media.eme.enabled", true);
user_pref("media.gmp-widevinecdm.enabled", true);
user_pref("media.gmp-widevinecdm.visible", true);
user_pref("browser.startup.homepage", "https://music.apple.com/es/home");
user_pref("browser.startup.page", 1);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("browser.tabs.warnOnClose", false);
user_pref("ui.systemUsesDarkTheme", 1);
user_pref("layout.css.prefers-color-scheme.content-override", 0);
user_pref("font.name.sans-serif.x-western", "Nimbus Sans");
user_pref("media.hardwaremediakeys.enabled", true);
// Violentmonkey (en extensions/) se activa sin preguntar; ejecuta local-music/local-music.user.js
user_pref("extensions.autoDisableScopes", 0);
user_pref("extensions.enabledScopes", 15);
