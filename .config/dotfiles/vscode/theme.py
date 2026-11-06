#!/usr/bin/env python3
"""Paint VS Code (Code - OSS) with the active theme's palette; it reloads settings.json by itself.

Everything comes from themes/current/theme.json, so a new theme needs nothing here.
`theme.py --test` checks every theme without touching the real settings.
"""
import json
import os
import sys
from pathlib import Path

THEMES = Path.home() / ".config/dotfiles/themes"
SETTINGS = Path.home() / ".config/Code - OSS/User/settings.json"


def rgb(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


def lum(c):
    r, g, b = (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in (x / 255 for x in rgb(c)))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def legible(c, bg, text):
    """Mix c towards the text colour until it reads on bg: palettes tuned for icons (blanco) are too pale for code."""
    a, b = rgb(c), rgb(text)
    for i in range(11):
        m = "#%02x%02x%02x" % tuple(round(x + (y - x) * i / 10) for x, y in zip(a, b))
        if contrast(m, bg) >= 4.5:
            return m
    return text


def theme_settings(theme):
    p = theme["palette"]
    bg0, bg, bg1, bg2, line = p["bg0"], p["bg"], p["bg1"], p["bg2"], p["line"]
    faint, muted, sub, text, acc = p["faint"], p["muted"], p["sub"], p["text"], p["accent"]
    code = {k: legible(p[k], bg0, text) for k in ("accent", "muted", "yellow", "orange", "red", "green", "teal", "blue")}

    colors = {
        "foreground": text, "descriptionForeground": muted, "focusBorder": acc, "errorForeground": code["red"],
        "textLink.foreground": code["accent"], "textLink.activeForeground": code["accent"],
        "editor.background": bg0, "editor.foreground": text,
        "editor.selectionBackground": acc + "40", "editor.lineHighlightBackground": bg1 + "80",
        "editorCursor.foreground": acc,
        "editorLineNumber.foreground": faint, "editorLineNumber.activeForeground": acc,
        "editorIndentGuide.background1": line, "editorWhitespace.foreground": line,
        "editorWidget.background": bg1, "editorWidget.border": line,
        "editorSuggestWidget.background": bg1, "editorHoverWidget.background": bg1,
        "editorError.foreground": code["red"], "editorWarning.foreground": code["yellow"],
        "editorInfo.foreground": code["blue"],
        "editorGroup.border": line, "editorGroupHeader.tabsBackground": bg,
        "tab.activeBackground": bg0, "tab.activeForeground": text, "tab.activeBorderTop": acc,
        "tab.inactiveBackground": bg, "tab.inactiveForeground": muted, "tab.border": line,
        "sideBar.background": bg, "sideBar.foreground": sub, "sideBar.border": line,
        "sideBarSectionHeader.background": bg1, "sideBarSectionHeader.foreground": sub,
        "activityBar.background": bg, "activityBar.foreground": acc, "activityBar.inactiveForeground": muted,
        "activityBar.border": line, "activityBarBadge.background": acc, "activityBarBadge.foreground": bg0,
        "statusBar.background": bg1, "statusBar.foreground": sub, "statusBar.border": line,
        "statusBar.noFolderBackground": bg1,
        "titleBar.activeBackground": bg, "titleBar.activeForeground": text,
        "titleBar.inactiveBackground": bg, "titleBar.inactiveForeground": muted,
        "panel.background": bg, "panel.border": line, "panelTitle.activeBorder": acc,
        "panelTitle.activeForeground": text, "panelTitle.inactiveForeground": muted,
        "list.activeSelectionBackground": bg2, "list.activeSelectionForeground": text,
        "list.inactiveSelectionBackground": bg1, "list.hoverBackground": bg1,
        "button.background": acc, "button.foreground": bg0, "button.hoverBackground": acc,
        "badge.background": acc, "badge.foreground": bg0,
        "input.background": bg1, "input.foreground": text, "input.border": line,
        "dropdown.background": bg1, "dropdown.foreground": text, "dropdown.border": line,
        "quickInput.background": bg1, "quickInput.foreground": text,
        "menu.background": bg1, "menu.foreground": text, "menu.selectionBackground": bg2,
        "gitDecoration.modifiedResourceForeground": code["yellow"],
        "gitDecoration.addedResourceForeground": code["green"],
        "gitDecoration.untrackedResourceForeground": code["green"],
        "gitDecoration.deletedResourceForeground": code["red"],
        "terminal.background": bg0, "terminal.foreground": text, "terminalCursor.foreground": acc,
        "terminal.ansiRed": code["red"], "terminal.ansiGreen": code["green"],
        "terminal.ansiYellow": code["yellow"], "terminal.ansiBlue": code["blue"],
        "terminal.ansiCyan": code["teal"], "terminal.ansiMagenta": code["accent"],
    }
    mono = f"'{theme['font_mono']}', monospace"
    return {
        # the base only fills what `colors` leaves out; azul is light for GTK but its palette is the dark terminal one
        "workbench.colorTheme": "Light Modern" if lum(bg0) > 0.5 else "Dark Modern",
        "workbench.colorCustomizations": colors,
        "editor.tokenColorCustomizations": {
            "comments": code["muted"], "keywords": code["accent"], "strings": code["green"],
            "numbers": code["orange"], "types": code["teal"], "functions": code["blue"], "variables": text,
        },
        "editor.fontFamily": mono,
        "terminal.integrated.fontFamily": mono,
    }


def apply(theme_json, settings):
    theme = json.loads(Path(theme_json).read_text())
    try:
        data = json.loads(settings.read_text() or "{}") if settings.exists() else {}
    except json.JSONDecodeError:
        # comments or trailing commas are valid for VS Code but not here: never rewrite what can't be parsed
        print(f"vscode: {settings} no es JSON puro; no lo toco", file=sys.stderr)
        return False
    data.update(theme_settings(theme))
    settings.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
    os.replace(tmp, settings)
    return True


def test():
    import tempfile
    jsons = [p / "theme.json" for p in THEMES.iterdir() if not p.is_symlink() and (p / "theme.json").exists()]
    assert jsons
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "User/settings.json"
        for j in jsons:
            f.parent.mkdir(exist_ok=True)
            f.write_text('{"claudeCode.hideOnboarding": true}')
            assert apply(j, f), j
            out = json.loads(f.read_text())
            assert out["claudeCode.hideOnboarding"] is True, "foreign keys must survive"
            bg0 = json.loads(j.read_text())["palette"]["bg0"]
            for k, c in out["editor.tokenColorCustomizations"].items():
                assert contrast(c, bg0) >= 4.5, (j.parent.name, k, c)
        bad = '{\n  // comment\n  "a": 1,\n}'
        f.write_text(bad)
        assert not apply(jsons[0], f) and f.read_text() == bad, "unparsable settings must stay intact"
    print(f"ok: {len(jsons)} temas")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        test()
    else:
        sys.exit(0 if apply(THEMES / "current/theme.json", SETTINGS) else 1)
