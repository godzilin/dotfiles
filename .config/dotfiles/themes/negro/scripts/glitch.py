#!/usr/bin/env python3
"""The tube loses sync for a moment on every workspace change: swaps crt.glsl for its GLITCH build and back.
Does nothing while the tube is off (Super+Shift+C).
  glitch.py          the daemon (theme.json "daemons")
  glitch.py --test   self-check"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CRT = Path.home() / ".config/dotfiles/themes/negro/hypr/crt.glsl"
GLITCH = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "crt-glitch.glsl"
LENGTH = 0.22  # seconds


def glitch_source(crt):
    """crt.glsl with GLITCH defined; #version has to stay on the first line."""
    first, rest = crt.split("\n", 1)
    return f"{first}\n#define GLITCH\n{rest}"


def changed_workspace(line):
    return line.startswith("workspacev2>>")


def set_shader(path):
    subprocess.run(["hyprctl", "eval", f'hl.config({{ decoration = {{ screen_shader = "{path}" }} }})'], capture_output=True)


def tube_on():
    out = subprocess.run(["hyprctl", "getoption", "decoration:screen_shader"], capture_output=True, text=True).stdout
    return "crt.glsl" in out


def daemon():
    GLITCH.write_text(glitch_source(CRT.read_text()))
    path = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{os.environ['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"
    with socket.socket(socket.AF_UNIX) as sock:
        sock.connect(path)
        lines = sock.makefile()
        for line in lines:
            if changed_workspace(line) and tube_on():
                set_shader(GLITCH)
                time.sleep(LENGTH)
                set_shader(CRT)


def test():
    out = glitch_source("#version 300 es\nvoid main() {}\n")
    assert out.split("\n")[:2] == ["#version 300 es", "#define GLITCH"]
    assert changed_workspace("workspacev2>>3,3\n") and not changed_workspace("activewindow>>a,b\n")
    print("ok")


if __name__ == "__main__":
    test() if sys.argv[1:] == ["--test"] else daemon()
