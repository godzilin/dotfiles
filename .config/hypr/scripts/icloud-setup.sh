#!/bin/sh
# One-off: store the iCloud CalDAV login in the keyring and do the first sync.
# Needs an app-specific password from https://account.apple.com (Sign-In and Security > App-Specific Passwords).
set -e
user=$(kdialog --title "iCloud" --inputbox "Apple ID (email):") || exit 1
pass=$(kdialog --title "iCloud" --password "Contraseña específica de app (xxxx-xxxx-xxxx-xxxx):") || exit 1
printf %s "$user" | secret-tool store --label="iCloud CalDAV user" service icloud-caldav field username
printf %s "$pass" | secret-tool store --label="iCloud CalDAV password" service icloud-caldav field password
mkdir -p ~/.local/share/vdirsyncer/icloud
yes | vdirsyncer discover icloud
vdirsyncer metasync
vdirsyncer sync
systemctl --user enable --now vdirsyncer.timer
khal printcalendars
notify-send "iCloud" "Calendario sincronizado"
