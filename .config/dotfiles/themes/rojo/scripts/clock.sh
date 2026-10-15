#!/bin/sh
# Bar clock: big time in Russo One, date in capitals ("JUE 15 OCT"); sed \U handles á/é in a UTF-8 locale
d=$(LC_TIME=es_ES.UTF-8 date '+%a %-d %b' | LC_ALL=es_ES.UTF-8 sed 's/.*/\U&/')
printf '<span font_family="Russo One" size="15pt">%s</span>   <span size="10pt">%s</span>\n' "$(date +%H:%M)" "$d"
