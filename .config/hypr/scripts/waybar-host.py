#!/usr/bin/env python3
"""Builds a per-monitor waybar config from the active theme's (see hosts/<hostname>-waybar.json).

The main bar is the theme's own bar with modules swapped by "replace" (null drops them); the secondary bar reuses
the theme's look and module definitions with its own module lists ("secondary": each slot lists alternatives,
the first one the theme defines wins) plus the extra "modules". "css" is added after the theme's style.css.
Prints the paths of the generated config and stylesheet.
Usage: waybar-host.py HOST.json [THEME_DIR] [OUT]   or   waybar-host.py --check HOST.json (every theme)
"""
import copy, json, os, re, sys

THEMES = os.path.expanduser("~/.config/dotfiles/themes")


def load_jsonc(path):
    out = []
    for line in open(path, encoding="utf-8"):
        quoted, i = False, 0
        while i < len(line):
            if line[i] == "\\" and quoted:
                i += 2
                continue
            if line[i] == '"':
                quoted = not quoted
            if not quoted and line[i:i + 2] == "//":
                line = line[:i] + "\n"
                break
            i += 1
        out.append(line)
    data = json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))
    return data[0] if isinstance(data, list) else data


def swap(names, replace):
    return [replace.get(n, n) for n in names if replace.get(n, n)]


def build(host, theme):
    replace = dict(host.get("replace", {}))
    bt = "/sys/class/bluetooth"
    if not (os.path.isdir(bt) and os.listdir(bt)):
        replace["bluetooth"] = None  # shortcut: checked when the bar starts; plug a dongle in and restart the bar
    main = copy.deepcopy(theme)
    main["output"] = host["main"]
    for key, value in main.items():
        if key.startswith("modules-") and isinstance(value, list):
            main[key] = swap(value, replace)
        elif key.startswith("group/") and isinstance(value, dict):
            value["modules"] = swap(value.get("modules", []), replace)
    for name, spec in host.get("modules", {}).items():
        main.setdefault(name, spec)

    sec_spec = host["secondary"]
    sec = copy.deepcopy(main)
    sec["output"] = sec_spec["output"]
    if sec.get("position") in ("left", "right"):  # a narrow vertical bar has no room for readings
        sec["position"] = "top"
        sec.pop("width", None)
        sec["height"] = sec_spec.get("height", 30)
    for side in ("left", "center", "right"):
        picked = [next((n for n in alts if n in sec), None) for alts in sec_spec.get(side, [])]
        sec["modules-" + side] = [n for n in picked if n]
    return [main, sec]


def main(argv):
    if argv[0] == "--check":
        host = json.load(open(argv[1]))
        gone = {k for k, v in host["replace"].items() if v is None} | set(host["replace"])
        for t in sorted(os.listdir(THEMES)):
            path = os.path.join(THEMES, t, "waybar", "config.jsonc")
            if t == "current" or not os.path.isfile(path):
                continue
            bars = build(host, load_jsonc(path))
            for bar in bars:
                used = [n for k, v in bar.items() if k.startswith("modules-") for n in v]
                used += [n for k, v in bar.items() if k.startswith("group/") for n in v.get("modules", [])]
                assert not gone & set(used), (t, gone & set(used))
                assert all(n in bar for n in used), (t, [n for n in used if n not in bar])
            assert "hyprland/workspaces" in bars[1]["modules-left"], t
            assert bars[1]["modules-center"], t
            print(t, "ok", bars[1]["modules-left"] + bars[1]["modules-center"] + bars[1]["modules-right"])
        return
    host = json.load(open(argv[0]))
    theme_dir = argv[1] if len(argv) > 1 else os.path.expanduser("~/.config/waybar")
    out = argv[2] if len(argv) > 2 else os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "waybar-host.json")
    json.dump(build(host, load_jsonc(os.path.join(theme_dir, "config.jsonc"))), open(out, "w"), ensure_ascii=False)
    css = os.path.splitext(out)[0] + ".css"
    with open(css, "w") as f:
        f.write('@import url("file://%s");\n%s\n' % (os.path.join(theme_dir, "style.css"), host.get("css", "")))
    print(out, css)


if __name__ == "__main__":
    main(sys.argv[1:])
