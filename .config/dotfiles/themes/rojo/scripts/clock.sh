#!/bin/sh
# Bar clock: big time in Russo One, date in Russian capitals ("ЧТ 15 ОКТ")
printf '<span font_family="Russo One" size="15pt">%s</span>   <span size="10pt">%s</span>\n' "$(date +%H:%M)" "$("$(dirname "$(readlink -f "$0")")/ru.sh" bar)"
