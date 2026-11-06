#!/usr/bin/env python3
"""Searchable list of the keyboard shortcuts (Super+F1): every bind with a description, read live from Hyprland, so
it follows binds.lua and the extras of each theme. Add `{ description = "..." }` to a bind to list it.
  atajos.py          show it in fuzzel
  atajos.py --test   self-check"""
import json
import subprocess
import sys

MODS = ((64, "Super"), (4, "Ctrl"), (8, "Alt"), (1, "Mayús"))
KEYS = {"masculine": "º", "Return": "Intro", "Prior": "RePág", "Next": "AvPág", "Print": "ImprPant",
        "BackSpace": "Retroceso", "Space": "Espacio", "Escape": "Esc", "Delete": "Supr", "left": "←", "right": "→",
        "up": "↑", "down": "↓", "mouse:272": "clic izquierdo", "mouse:273": "clic derecho"}


def combo(bind):
    return "+".join([name for bit, name in MODS if bind["modmask"] & bit] + [KEYS.get(bind["key"], bind["key"])])


def shown(keys):
    """Super+Q, or Super+←/→ and Super+1…9 for the same bind on several keys."""
    head, tails = zip(*(k.rpartition("+")[::2] for k in keys))
    if len(set(head)) > 1:
        return " / ".join(keys)
    prefix = head[0] + "+" if head[0] else ""
    return prefix + (f"{tails[0]}…{tails[-1]}" if len(tails) > 4 else "/".join(tails))


def lines(binds):
    """One line per description."""
    grouped = {}
    for b in binds:
        if b["has_description"] and not b["submap"]:
            grouped.setdefault(b["description"], []).append(combo(b))
    rows = [(shown(keys), description) for description, keys in grouped.items()]
    width = max(len(keys) for keys, _ in rows)
    return [f"{keys:<{width + 3}}{description}" for keys, description in rows]


def main():
    binds = json.loads(subprocess.run(["hyprctl", "binds", "-j"], capture_output=True, text=True).stdout)
    text = "\n".join(lines(binds))
    # shortcut: pressing Intro just closes the list, it does not run the shortcut
    subprocess.run(["fuzzel", "--dmenu", "--prompt", "  ", "--placeholder", "Buscar atajo", "--lines", "24", "--width", "78"],
                   input=text, text=True, capture_output=True)


def test():
    b = lambda key, mask, desc, sub="": {"key": key, "modmask": mask, "has_description": bool(desc), "description": desc, "submap": sub}
    assert combo(b("Q", 64, "x")) == "Super+Q" and combo(b("left", 65, "x")) == "Super+Mayús+←"
    out = lines([b("1", 64, "Ir"), *[b(str(i), 64, "Ir") for i in range(2, 10)], b("Q", 64, "Cerrar"), b("F4", 8, "Cerrar"),
                 b("X", 64, ""), b("left", 0, "No", "resize")])
    assert len(out) == 2 and "Super+1…9" in out[0] and "Super+Q / Alt+F4" in out[1], out
    assert shown(["Super+←", "Super+→"]) == "Super+←/→"
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        test()
    elif subprocess.run(["pkill", "-x", "fuzzel"]).returncode:  # the key closes it when already open
        main()
