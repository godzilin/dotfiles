#!/bin/sh
# claude-estado.sh on|off: hook de Claude Code. Marca la sesion del JSON de stdin como pensando.
d="${XDG_RUNTIME_DIR:-/tmp}/claude-estado"; mkdir -p "$d"
s=$(jq -r '.session_id // "x"'); s=${s##*/}
case "$1" in on) : > "$d/$s";; off) rm -f "$d/$s";; esac
