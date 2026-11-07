#!/usr/bin/env python3
"""Paint the "camaleon" theme from an image: python3 generar.py IMAGE

Takes the image's dominant hue, builds the usual 16-colour palette around it (dark backgrounds tinted with that hue,
the accent in it, the semantic colours nudged towards it) and renders plantilla/ into the theme folder, plus
theme.json and a fastfetch logo cut out of the image. Everything it writes is untracked: the repo keeps only plantilla/.
scripts/fondo.py calls it every time the wallpaper changes."""
import colorsys
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
TPL = HERE / "plantilla"

# (lightness, saturation) in HLS for the tones that follow the image's hue
TONES = {
    "bg0": (0.055, 0.30), "bg": (0.08, 0.28), "bg1": (0.11, 0.25), "bg2": (0.145, 0.22),
    "line": (0.22, 0.20), "faint": (0.31, 0.16), "muted": (0.52, 0.13), "sub": (0.73, 0.18), "text": (0.91, 0.25),
}
# Semantic colours keep their meaning; their hue is pulled a little towards the image's
SEMANTIC = {"red": 0.0, "orange": 0.07, "yellow": 0.125, "green": 0.33, "teal": 0.48, "blue": 0.60}


def dominant(img):
    """(hue, colourfulness 0..1) of the most present saturated hue: a 36-bin histogram weighted by chroma."""
    small = img.convert("RGB").resize((96, 96))
    px = getattr(small, "get_flattened_data", small.getdata)()  # getdata goes away in Pillow 14
    bins, total = [0.0] * 36, 0.0
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        w = s * v  # grey and dark pixels hardly vote
        bins[int(h * 36) % 36] += w
        total += w
    i = max(range(36), key=lambda k: bins[k - 1] + bins[k] + bins[(k + 1) % 36])
    return (i + 0.5) / 36, min(1.0, total / len(px) * 3)


def hls(h, l, s):
    return "%02x%02x%02x" % tuple(round(c * 255) for c in colorsys.hls_to_rgb(h % 1, l, s))


def palette(img):
    h, chroma = dominant(img)
    k = 0.35 + 0.65 * chroma  # a grey photo gives a grey theme, not a garish one
    p = {name: hls(h, l, s * k) for name, (l, s) in TONES.items()}
    p["accent"] = hls(h, 0.68, 0.62 * k + 0.1)
    for name, hue in SEMANTIC.items():
        d = (h - hue + 0.5) % 1 - 0.5  # shortest way round the colour wheel
        p[name] = hls(hue + d * 0.05, 0.68, 0.55)
    for i, l in enumerate((0.80, 0.68, 0.55, 0.40)):
        p[f"stripe{i}"] = hls(h, l, 0.55 * k + 0.1)
    return p


def render(text, p, wallpaper):
    def sub(m):
        key, part = m[1], m[2]
        if key == "wallpaper":
            return wallpaper
        if part:
            return str(int(p[key][{"r": 0, "g": 2, "b": 4}[part]:][:2], 16))
        return p[key]
    return re.sub(r"\{\{(\w+)(?:\.([rgb]))?\}\}", sub, text)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)  # atomic: alacritty, swaync... never read half a file


def logo(img, bg):
    """The Arch logo filled with the wallpaper, as fastfetch half blocks over the terminal's background bg."""
    sys.path.insert(0, str(HERE.parent.parent))
    import logolib as L
    rows2, cols = 38, 46
    canvas = Image.new("RGBA", L.size(cols, rows2, 4), (0, 0, 0, 0))
    mask = L.arch(int(canvas.height * 0.94))
    fill = img.convert("RGBA").resize(mask.size)
    fill.putalpha(mask)
    canvas.alpha_composite(fill, ((canvas.width - fill.width) // 2, (canvas.height - fill.height) // 2))
    rgb = tuple(int(bg[i:i + 2], 16) for i in (0, 2, 4))
    L.write(HERE / "fastfetch/logo.txt", L.blocks(canvas, cols, rows2, rgb))


def main(image):
    img = Image.open(image)
    img.seek(0)  # animated GIF previews: first frame
    p = palette(img)
    for f in TPL.rglob("*"):
        if f.is_file() and f.name != "theme.json":
            write(HERE / f.relative_to(TPL), render(f.read_text(), p, str(image)))
    j = json.loads((TPL / "theme.json").read_text())
    j["palette"] = {k: "#" + v for k, v in p.items() if not k.startswith("stripe")}
    j["stripes"] = ["#" + p[f"stripe{i}"] for i in range(4)]
    write(HERE / "theme.json", json.dumps(j, indent=2, ensure_ascii=False) + "\n")
    try:
        logo(img, p["bg"])
    except Exception as e:  # cosmetic: fastfetch keeps the previous logo
        print("generar: logo:", e, file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).expanduser().resolve())
