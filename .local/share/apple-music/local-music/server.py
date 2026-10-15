#!/usr/bin/env python3
"""Sirve ~/Music a la app de Apple Music (userscript local-music.user.js).

Solo escucha en 127.0.0.1. Rutas:
  /index.json            lista de pistas con tags (ffprobe, cacheado por mtime)
  /cover?f=<ruta>        portada embebida en JPEG (ffmpeg)
  /local-music.user.js   el userscript, para instalarlo/actualizarlo en Violentmonkey
  /<ruta>                el archivo de audio
"""
import json
import os
import subprocess
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PORT = 47823
MUSIC = Path(os.environ.get("LOCAL_MUSIC_DIR", Path.home() / "Music")).resolve()
HERE = Path(__file__).resolve().parent
AUDIO = {".flac", ".mp3", ".m4a", ".ogg", ".opus", ".wav", ".aac"}
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

_tags = {}  # ruta -> (mtime, dict)


def probe(path):
    mtime = path.stat().st_mtime
    hit = _tags.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-of", "json", "-show_entries",
         "format=duration:format_tags:stream=codec_type", str(path)],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    fmt = data.get("format", {})
    tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
    rel = path.relative_to(MUSIC).as_posix()
    info = {
        "path": rel,
        "title": tags.get("title") or path.stem,
        "artist": tags.get("artist") or tags.get("album_artist") or "",
        "album": tags.get("album") or path.parent.name,
        "track": int(str(tags.get("track", "0")).split("/")[0] or 0),
        "year": tags.get("date", "")[:4],
        "duration": float(fmt.get("duration") or 0),
        "cover": any(s.get("codec_type") == "video" for s in data.get("streams", [])),
    }
    _tags[path] = (mtime, info)
    return info


def index():
    files = sorted(p for p in MUSIC.rglob("*") if p.suffix.lower() in AUDIO and p.is_file())
    return [probe(p) for p in files]


class Handler(SimpleHTTPRequestHandler):
    def send_body(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Contra DNS rebinding: una web con un dominio apuntando a 127.0.0.1 no puede leer la música
        if self.headers.get("Host") not in ALLOWED_HOSTS:
            return self.send_error(403)
        url = urlparse(self.path)
        if url.path == "/index.json":
            return self.send_body(json.dumps(index()).encode(), "application/json; charset=utf-8")
        if url.path == "/local-music.user.js":
            return self.send_body((HERE / "local-music.user.js").read_bytes(), "text/javascript; charset=utf-8")
        if url.path == "/cover":
            rel = parse_qs(url.query).get("f", [""])[0]
            path = (MUSIC / rel).resolve()
            if not path.is_relative_to(MUSIC) or not path.is_file():
                return self.send_error(404)
            jpg = subprocess.run(
                ["ffmpeg", "-v", "quiet", "-i", str(path), "-an", "-frames:v", "1",
                 "-vf", "scale=600:-1", "-f", "image2", "-c:v", "mjpeg", "-"],
                capture_output=True).stdout
            return self.send_body(jpg, "image/jpeg") if jpg else self.send_error(404)
        return super().do_GET()

    def list_directory(self, path):
        return self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if "--test" in sys.argv:
        tracks = index()
        assert tracks and all(t["title"] for t in tracks), tracks
        print(f"{len(tracks)} pistas, ej.: {tracks[0]}")
        sys.exit()
    ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(MUSIC))).serve_forever()
