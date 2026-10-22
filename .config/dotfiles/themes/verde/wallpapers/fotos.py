#!/usr/bin/env python3
"""Real nature photos for the "verde" rotation, from Wikimedia Commons (featured pictures, free licences).
Each one is cropped to the screen and gets a small caption in the bottom-right corner: the place, and the
author and licence (CC BY-SA asks for that credit). Run: python3 fotos.py   (writes rotation/p-*.jpg)"""
import html
import json
import re
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1200
HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
API = "https://commons.wikimedia.org/w/api.php"
UA = "godzilin-dotfiles/1.0 (personal wallpapers; https://github.com/godzilin/dotfiles)"

# (output name, Commons file, caption, horizontal focus 0..1 for the crop)
PHOTOS = [
    ("p01-garajonay", "Bosque Encantado, Parque nacional de Garajonay, La Gomera, España, 2012-12-14, DD 19.jpg",
     "Laurisilva · Bosque Encantado, Garajonay (La Gomera)", 0.5),
    ("p02-fanal", "Fanal (Madeira, Portugal), Lorbeerwald -- 2025 -- 1532.jpg", "Laurisilva · Fanal, Madeira", 0.5),
    ("p03-fanal-niebla", "Foggy Fanal forest in Seixal, Porto Moniz, Madeira, 2023 May.jpg",
     "Laurisilva en la niebla · Fanal, Madeira", 0.5),
    ("p04-fanal-til", "Fanal (Madeira, Portugal), Lorbeerwald -- 2025 -- 1546.jpg", "Tiles centenarios · Fanal, Madeira", 0.5),
    ("p05-teide", "Roque Cinchado mit Teide.jpg", "Roque Cinchado y Teide · Tenerife", 0.5),
    ("p06-agando", "La Gomera - Roque Agando.jpg", "Roque de Agando · La Gomera", 0.5),
    ("p07-otway", "Beech Forest (AU), Great Otway National Park, Beauchamp Falls -- 2019 -- 1271.jpg",
     "Selva templada · Beauchamp Falls, Great Otway (Australia)", 0.5),
    ("p10-gullmarsskogen", "Beech and ferns in Gullmarsskogen.jpg", "Hayas y helechos · Gullmarsskogen (Suecia)", 0.5),
    ("p11-mons-klint", "Møns Klint beech trees in gorge 2015-04-01-4864.jpg", "Hayedo en primavera · Møns Klint (Dinamarca)", 0.5),
    ("p12-sequoia", "Giant sequoias in Sequoia National Park 2013.jpg", "Secuoyas gigantes · Sequoia (California)", 0.5),
    ("p13-metasequoia", "Forest of metasequoia glyptostroboides at Nagai Botanical Garden, February 2024 - 8010.jpg",
     "Bosque de metasecuoyas · Osaka (Japón)", 0.5),
    ("p14-yosemite", "Tunnel View, Yosemite Valley, Yosemite NP - Diliff.jpg", "Tunnel View · Yosemite (California)", 0.5),
    ("p15-geiranger", "Fiordo de Geiranger desde Flydalsjuvet, Noruega, 2019-09-07, DD 59.jpg",
     "Fiordo de Geiranger · Noruega", 0.5),
    ("p16-gavarnie", "2019 - Parc national des Pyrenees - Vallée de Gavarnie.jpg", "Valle de Gavarnie · Pirineos", 0.5),
    ("p17-cornion", "Macizo del Corniòn.jpg", "Macizo del Cornión · Picos de Europa", 0.5),
    ("p18-reine", "Moltbærtinden and Breiflogtinden over Reinevågen in Moskenes, Nordland, Norway, 2022 June.jpg",
     "Reinevågen · Lofoten (Noruega)", 0.5),
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


def cover(img, focus):
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - W) * focus)
    y = (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def caption(img, place, credit):
    big = ImageFont.truetype(str(FONTS / "nunito-700-normal.ttf"), 17)
    small = ImageFont.truetype(str(FONTS / "nunito-400-normal.ttf"), 12)
    pin = "     "  # room for the dot, drawn below (Nunito has no such glyph)
    d = ImageDraw.Draw(img)
    w1 = d.textlength(pin + place, font=big)
    w2 = d.textlength(credit, font=small)
    right, bottom = W - 34, H - 28
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))  # soft dark halo so it reads on any photo
    sd = ImageDraw.Draw(shadow)
    sd.text((right - w1, bottom - 42), pin + place, font=big, fill=(0, 0, 0, 200))
    sd.text((right - w2, bottom - 16), credit, font=small, fill=(0, 0, 0, 200))
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(img)
    cx, cy = right - w1 + 7, bottom - 42 + 12
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(156, 194, 107, 255))
    d.text((right - w1 + d.textlength(pin, font=big), bottom - 42), place, font=big, fill=(228, 230, 208, 235))
    d.text((right - w2, bottom - 16), credit, font=small, fill=(228, 230, 208, 170))
    return img.convert("RGB")


def main():
    out = HERE / "rotation"
    out.mkdir(exist_ok=True)
    credits = []
    for name, title, place, focus in PHOTOS:
        dest = out / f"{name}.jpg"
        url, artist, lic = info(title)
        credit = f"Foto: {artist} · {lic} · Wikimedia Commons"
        credits.append(f"- {name}.jpg: [{title}](https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title.replace(' ', '_'))})"
                       f" — {artist}, {lic}")
        if not dest.exists():
            img = Image.open(BytesIO(get(url))).convert("RGB")
            caption(cover(img, focus), place, credit).save(dest, quality=88, optimize=True, progressive=True)
            print("wrote", dest.name)
        time.sleep(2)
    (HERE / "FOTOS.md").write_text("# Fotos de la rotación de verde\n\nDe Wikimedia Commons; cada una lleva su crédito "
                                   "en la esquina.\n\n" + "\n".join(credits) + "\n")


if __name__ == "__main__":
    main()
