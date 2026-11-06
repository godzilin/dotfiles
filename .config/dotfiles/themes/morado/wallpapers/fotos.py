#!/usr/bin/env python3
"""Real night photos of Tokyo for the "morado" rotation, from Wikimedia Commons (free licences, no NC/ND).
Each one is cropped to the screen and its shadows graded towards the theme's violet; no text on the image, the
credits go to FOTOS.md. Run: python3 fotos.py   (writes rotation/p-*.jpg and FOTOS.md)"""
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 1920, 1200
HERE = Path(__file__).resolve().parent
API = "https://commons.wikimedia.org/w/api.php"
UA = "godzilin-dotfiles/1.0 (personal wallpapers; https://github.com/godzilin/dotfiles)"
SHADOW = np.array((21, 16, 42), np.float32)  # palette "bg"

PHOTOS = [
    ("p01-avenida", "2024-10-20 Shinjuku at night 1.jpg"),
    ("p02-cruce", "2024-10-20 Shinjuku at night 2.jpg"),
    ("p03-carteles", "Colorful neon street signs in Kabukichō, Shinjuku, Tokyo.jpg"),
    ("p04-estelas", "Night in Shinjuku 2.JPG"),
    ("p05-kabukicho", "Shinjuku, night, May 2017.jpg"),
    ("p06-azul", "Shinjuku at night, August 2019.jpg"),
    ("p07-paraguas", "Kabukicho (53084208713).jpg"),
    ("p08-coches", "Shinjuku Kabukicho night lights 2016-12-04.jpg"),
    ("p09-horizonte", "Roppongi at night seen from Shibuya Stream.jpg"),
    ("p10-lluvia", "Evening downpour near Tokyo Tower in Tokyo, 20240821 1915 5342.jpg"),
    ("p11-charcos", "Evening downpour near Tokyo Tower in Tokyo, 20240821 1915 5347.jpg"),
    ("p12-calle-mojada", "Walking around Kabukicho, Shinjuku at night. (29362321701).jpg"),
    ("p14-puente", "Tokyo 2018 (41491807354).jpg"),
    ("p15-skytree", "Tokyo Skytree DSC05774.jpg"),
    ("p16-torre", "Tokyo Tower at night (51473476907).jpg"),
    ("p17-ginza", "Ginza at night.jpg"),
    ("p18-farolillos", "Fureai Road in Nakano, Tokyo, Japan, 2024 May.jpg"),
    ("p19-callejon-mojado", "Manten @ Jimbocho (11869609083).jpg"),
]


def get(url):
    for wait in (0, 5, 15, 30):
        time.sleep(wait)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError(f"rate limited: {url}")


def info(title):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": "File:" + title, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "iiurlwidth": 3840,
                                "iiextmetadatafilter": "Artist|LicenseShortName"})
    page = next(iter(json.loads(get(f"{API}?{q}"))["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    meta = ii["extmetadata"]
    artist = html.unescape(re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", ""))).strip()
    return ii.get("thumburl") or ii["url"], re.sub(r"\s+", " ", artist), meta["LicenseShortName"]["value"]


def cover(img):
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def grade(img):
    """Blacks lift to the theme's night, highlights stay as they are."""
    a = np.asarray(img, np.float32)
    dark = (1 - a.mean(axis=2, keepdims=True) / 255) ** 2.5
    return Image.fromarray((a * (1 - dark) + SHADOW * dark).clip(0, 255).astype(np.uint8))


def main():
    out = ["# Fotos de la rotación de morado", "",
           "De Wikimedia Commons; recortadas y con las sombras teñidas de violeta.", ""]
    for name, title in PHOTOS:
        url, artist, licence = info(title)
        grade(cover(Image.open(BytesIO(get(url))).convert("RGB"))).save(HERE / "rotation" / f"{name}.jpg", quality=86)
        page = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title.replace(" ", "_"))
        out.append(f"- {name}.jpg: [{title}]({page}) — {artist}, {licence}")
        print(name, flush=True)
    (HERE / "FOTOS.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
