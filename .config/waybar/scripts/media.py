#!/usr/bin/env python3
"""Waybar now-playing module (custom/media, return-type json).
Prints `TITLE · ARTIST  ▮▮▮▯▯ -1:42` whenever the player changes and every second while playing.
Also keeps ~/.cache/nostromo/cover-path pointing at the current album art for the image#cover module."""
import hashlib
import json
import os
import subprocess
import urllib.request

import gi

gi.require_version("Playerctl", "2.0")
from gi.repository import GLib, Playerctl  # noqa: E402

CACHE = os.path.expanduser("~/.cache/nostromo")
COVER_PATH_FILE = os.path.join(CACHE, "cover-path")
COVER_SIGNAL = 8  # image#cover listens on SIGRTMIN+8
manager = Playerctl.PlayerManager()
last_cover = None


def current_player():
    """The player that is playing, else the most recent one."""
    players = manager.props.players
    for p in players:
        if p.props.playback_status == Playerctl.PlaybackStatus.PLAYING:
            return p
    return players[0] if players else None


def clock(us):
    s = max(int(us // 1_000_000), 0)
    return f"{s // 60}:{s % 60:02d}"


def cover_file(url):
    """Local path for an mpris:artUrl (file:// used as is, http(s) downloaded once)."""
    if not url:
        return ""
    if url.startswith("file://"):
        return urllib.request.url2pathname(url[7:])
    if url.startswith("http"):
        path = os.path.join(CACHE, "covers", hashlib.md5(url.encode()).hexdigest())
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                urllib.request.urlretrieve(url, path)
            except OSError:
                return ""
        return path
    return ""


def cmus_cover():
    """cmus sends no mpris:artUrl: extract the art embedded in the playing file (cached per file)."""
    try:
        status = subprocess.run(["cmus-remote", "-Q"], capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""
    song = next((line[5:] for line in status.splitlines() if line.startswith("file ")), "")
    if not song:
        return ""
    path = os.path.join(CACHE, "covers", hashlib.md5(song.encode()).hexdigest() + ".jpg")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", song, "-an", "-frames:v", "1", path],
                       capture_output=True, timeout=10)
    return path if os.path.exists(path) else ""


def set_cover(path):
    global last_cover
    if path == last_cover:
        return
    last_cover = path
    os.makedirs(CACHE, exist_ok=True)
    with open(COVER_PATH_FILE, "w") as f:
        f.write(path)
    subprocess.run(["pkill", f"-RTMIN+{COVER_SIGNAL}", "-x", "waybar"])


def emit(*_):
    p = current_player()
    if not p:
        print(json.dumps({"text": "", "class": "stopped"}), flush=True)
        set_cover("")
        return True
    meta = p.props.metadata.unpack() if p.props.metadata else {}
    title = meta.get("xesam:title") or "—"
    artist = ", ".join(meta.get("xesam:artist") or []) or p.props.player_name
    length = meta.get("mpris:length") or 0
    try:
        pos = p.get_position()
    except GLib.Error:
        pos = 0
    playing = p.props.playback_status == Playerctl.PlaybackStatus.PLAYING

    esc = GLib.markup_escape_text
    text = f"{esc(title[:28])}{'…' if len(title) > 28 else ''} <span color='#857c69'>· {esc(artist[:18])}</span>"
    if length:
        filled = min(round(8 * pos / length), 8)
        bar = f"<span color='#e9a23b'>{'▮' * filled}</span><span color='#3d382d'>{'▮' * (8 - filled)}</span>"
        text += f"  {bar} <span color='#b3a891'>-{clock(length - pos)}</span>"
    print(json.dumps({"text": text, "class": "playing" if playing else "paused",
                      "tooltip": f"{title}\n{artist}"}), flush=True)
    art = cover_file(meta.get("mpris:artUrl", ""))
    if not art and p.props.player_name == "cmus":
        art = cmus_cover()
    set_cover(art)
    return True


def watch(name):
    player = Playerctl.Player.new_from_name(name)
    for signal in ("playback-status", "metadata", "seeked"):
        player.connect(signal, emit)
    manager.manage_player(player)


manager.connect("name-appeared", lambda _m, name: (watch(name), emit()))
manager.connect("player-vanished", lambda *_: emit())
for name in manager.props.player_names:
    watch(name)

emit()
GLib.timeout_add_seconds(1, emit)
GLib.MainLoop().run()
