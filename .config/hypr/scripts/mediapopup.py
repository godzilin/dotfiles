#!/usr/bin/env python3
"""Nostromo now-playing popup (opened from the waybar media module).
Big cover, title/artist/album, seekable progress, shuffle/prev/play/next/loop and player volume.
Live via Playerctl signals plus a 1 s tick. Esc closes; a click outside closes it too (hypr/binds.lua)."""
import os
import sys
import urllib.request

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Playerctl", "2.0")
from gi.repository import GdkPixbuf, GLib, Gtk, Playerctl  # noqa: E402

GLib.set_prgname("nostromo-media")  # Wayland app_id, matched by the window rule

CSS = b"""
window { background: #1a1814; }
* { font-family: "BlexMono Nerd Font", monospace; color: #b3a891; letter-spacing: 1px; }
.head { font-size: 9pt; color: #857c69; }
.head-dot { color: #e9a23b; }
.stripe-1 { background: #e0c36a; } .stripe-2 { background: #e9a23b; }
.stripe-3 { background: #d9652b; } .stripe-4 { background: #c8553d; }
.cover { border: 1px solid #3d382d; border-radius: 8px; background: #24211b; }
.title { font-family: "IBM Plex Sans", sans-serif; font-size: 13pt; font-weight: 600; color: #e8dfc8; letter-spacing: 0; }
.artist { font-size: 10pt; color: #b3a891; }
.album { font-size: 9pt; color: #857c69; }
.time { font-size: 9pt; color: #857c69; }
scale trough { background: #2f2b23; min-height: 4px; border-radius: 2px; border: none; }
scale highlight { background: #e9a23b; border-radius: 2px; }
scale slider { background: #e8dfc8; min-width: 10px; min-height: 10px; border-radius: 5px; margin: -4px; border: none; box-shadow: none; }
button { background: transparent; border: none; box-shadow: none; border-radius: 8px; padding: 4px 10px; }
button label { font-size: 16pt; color: #b3a891; }
button:hover { background: #2f2b23; }
button:hover label { color: #e8dfc8; }
button.main { background: #e9a23b; }
button.main label { color: #121110; }
button.main:hover { background: #e0c36a; }
button.on label { color: #e9a23b; }
.vol-label { font-size: 9pt; color: #857c69; }
"""

ICONS = {"prev": "󰒮", "next": "󰒭", "play": "󰐊", "pause": "󰏤", "shuffle": "󰒝", "noshuffle": "󰒞",
         "loop-none": "󰑗", "loop-track": "󰑘", "loop-playlist": "󰑖"}
COVER = 132


def clock(us):
    s = max(int(us // 1_000_000), 0)
    return f"{s // 60}:{s % 60:02d}"


class Popup(Gtk.Window):
    def __init__(self):
        super().__init__(title="Now playing")
        self.manager = Playerctl.PlayerManager()
        self.player = None
        self.seeking = False
        self.cover_url = None

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=18)
        self.add(root)

        head = Gtk.Box(spacing=6)
        dot = Gtk.Label(label="󰯈"); dot.get_style_context().add_class("head-dot")
        self.head = Gtk.Label(xalign=0); self.head.get_style_context().add_class("head")
        head.pack_start(dot, False, False, 0); head.pack_start(self.head, True, True, 0)
        root.pack_start(head, False, False, 0)
        stripes = Gtk.Box(homogeneous=True)
        for i in range(1, 5):
            bar = Gtk.Box(); bar.set_size_request(-1, 3); bar.get_style_context().add_class(f"stripe-{i}")
            stripes.pack_start(bar, True, True, 0)
        root.pack_start(stripes, False, False, 0)

        body = Gtk.Box(spacing=16, margin_top=6)
        self.cover = Gtk.Image(); self.cover.set_size_request(COVER, COVER)
        frame = Gtk.Box(); frame.get_style_context().add_class("cover"); frame.pack_start(self.cover, True, True, 0)
        body.pack_start(frame, False, False, 0)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, valign=Gtk.Align.CENTER)
        self.title = self._label("title", lines=2)
        self.artist = self._label("artist")
        self.album = self._label("album")
        for w in (self.title, self.artist, self.album):
            text.pack_start(w, False, False, 0)
        body.pack_start(text, True, True, 0)
        root.pack_start(body, False, False, 0)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.scale.set_draw_value(False)
        self.scale.connect("button-press-event", lambda *_: setattr(self, "seeking", True))
        self.scale.connect("button-release-event", self._seek)
        root.pack_start(self.scale, False, False, 0)
        times = Gtk.Box()
        self.elapsed = self._label("time"); self.remaining = self._label("time")
        self.remaining.set_xalign(1)
        times.pack_start(self.elapsed, True, True, 0); times.pack_start(self.remaining, True, True, 0)
        root.pack_start(times, False, False, 0)

        controls = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
        self.b_shuffle = self._button(self._shuffle)
        self.b_prev = self._button(lambda: self.player and self.player.previous())
        self.b_play = self._button(lambda: self.player and self.player.play_pause(), "main")
        self.b_next = self._button(lambda: self.player and self.player.next())
        self.b_loop = self._button(self._loop)
        for b in (self.b_shuffle, self.b_prev, self.b_play, self.b_next, self.b_loop):
            controls.pack_start(b, False, False, 0)
        root.pack_start(controls, False, False, 0)

        vol = Gtk.Box(spacing=10)
        label = Gtk.Label(label="VOL"); label.get_style_context().add_class("vol-label")
        self.volume = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.05)
        self.volume.set_draw_value(False)
        self.volume.connect("value-changed", self._set_volume)
        vol.pack_start(label, False, False, 0); vol.pack_start(self.volume, True, True, 0)
        root.pack_start(vol, False, False, 0)

        self.connect("key-press-event", lambda _w, e: e.keyval == 0xff1b and Gtk.main_quit())
        self.connect("destroy", Gtk.main_quit)
        self.manager.connect("name-appeared", lambda _m, name: self._watch(name))
        self.manager.connect("player-vanished", lambda *_: self.refresh())
        for name in self.manager.props.player_names:
            self._watch(name)
        self.refresh()
        GLib.timeout_add_seconds(1, self.tick)

    def _label(self, cls, lines=1):
        label = Gtk.Label(xalign=0, ellipsize=3, max_width_chars=26, lines=lines)
        if lines > 1:
            label.set_line_wrap(True)
        label.get_style_context().add_class(cls)
        return label

    def _button(self, action, cls=None):
        b = Gtk.Button(label="")
        if cls:
            b.get_style_context().add_class(cls)
        b.connect("clicked", lambda *_: (action(), GLib.timeout_add(150, self.refresh)))
        return b

    def _watch(self, name):
        player = Playerctl.Player.new_from_name(name)
        for signal in ("playback-status", "metadata", "seeked", "shuffle", "loop-status", "volume"):
            player.connect(signal, lambda *_: self.refresh())
        self.manager.manage_player(player)
        self.refresh()

    def _pick(self):
        players = self.manager.props.players
        for p in players:
            if p.props.playback_status == Playerctl.PlaybackStatus.PLAYING:
                return p
        return players[0] if players else None

    def _seek(self, *_):
        self.seeking = False
        if self.player:
            try:
                self.player.set_position(int(self.scale.get_value()))
            except GLib.Error:
                pass

    def _shuffle(self):
        if self.player:
            try:
                self.player.set_shuffle(not self.player.props.shuffle)
            except GLib.Error:
                pass

    def _loop(self):
        if self.player:
            order = [Playerctl.LoopStatus.NONE, Playerctl.LoopStatus.PLAYLIST, Playerctl.LoopStatus.TRACK]
            try:
                now = order.index(self.player.props.loop_status)
                self.player.set_loop_status(order[(now + 1) % 3])
            except (GLib.Error, ValueError):
                pass

    def _set_volume(self, scale):
        if self.player and not self.updating:
            try:
                self.player.set_volume(scale.get_value())
            except GLib.Error:
                pass

    def _set_cover(self, url):
        if url == self.cover_url:
            return
        self.cover_url = url
        path = None
        if url.startswith("file://"):
            path = urllib.request.url2pathname(url[7:])
        elif url.startswith("http"):
            try:
                path, _ = urllib.request.urlretrieve(url)
            except OSError:
                path = None
        if path and os.path.exists(path):
            pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, COVER, COVER, True)
            self.cover.set_from_pixbuf(pix)
        else:
            self.cover.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)

    def refresh(self):
        self.updating = True
        self.player = p = self._pick()
        if not p:
            self.head.set_text("SIN REPRODUCCIÓN")
            for w in (self.title, self.artist, self.album, self.elapsed, self.remaining):
                w.set_text("")
            self.title.set_text("Nada sonando")
            self._set_cover("")
            self.updating = False
            return False
        meta = p.props.metadata.unpack() if p.props.metadata else {}
        playing = p.props.playback_status == Playerctl.PlaybackStatus.PLAYING
        self.head.set_text(f"{'NOW PLAYING' if playing else 'EN PAUSA'} · {p.props.player_name.upper()}")
        self.title.set_text(meta.get("xesam:title") or "—")
        self.artist.set_text(", ".join(meta.get("xesam:artist") or []))
        self.album.set_text(meta.get("xesam:album") or "")
        self._set_cover(meta.get("mpris:artUrl", ""))
        self.length = meta.get("mpris:length") or 0
        self.scale.set_range(0, max(self.length, 1))
        self.scale.set_sensitive(bool(self.length) and p.props.can_seek)

        self.b_play.set_label(ICONS["pause" if playing else "play"])
        self.b_prev.set_label(ICONS["prev"]); self.b_next.set_label(ICONS["next"])
        try:
            shuffle = p.props.shuffle
        except GLib.Error:
            shuffle = False
        self.b_shuffle.set_label(ICONS["shuffle" if shuffle else "noshuffle"])
        self.b_shuffle.get_style_context().remove_class("on")
        if shuffle:
            self.b_shuffle.get_style_context().add_class("on")
        loop = {Playerctl.LoopStatus.TRACK: "loop-track", Playerctl.LoopStatus.PLAYLIST: "loop-playlist"}.get(
            p.props.loop_status, "loop-none")
        self.b_loop.set_label(ICONS[loop])
        self.b_loop.get_style_context().remove_class("on")
        if loop != "loop-none":
            self.b_loop.get_style_context().add_class("on")
        self.volume.set_value(p.props.volume)
        self.tick()
        self.updating = False
        return False

    def tick(self):
        if self.player and not self.seeking:
            try:
                pos = self.player.get_position()
            except GLib.Error:
                pos = 0
            self.scale.set_value(pos)
            self.elapsed.set_text(clock(pos))
            self.remaining.set_text(f"-{clock(self.length - pos)}" if self.length else "")
        return True


if __name__ == "__main__":
    win = Popup()
    win.updating = False
    win.show_all()
    if "--shot" in sys.argv:  # close by itself, for screenshots
        GLib.timeout_add_seconds(4, Gtk.main_quit)
    Gtk.main()
