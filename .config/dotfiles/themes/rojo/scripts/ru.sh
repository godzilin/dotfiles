#!/bin/sh
# Russian words for the rojo theme without a ru_RU locale:
#   ru.sh bar   -> "ЧТ 15 ОКТ"            ru.sh lock -> "ЧЕТВЕРГ 15 ОКТЯБРЯ"
#   ru.sh name  -> the user's name in Cyrillic capitals (simple transliteration: Dani -> ДАНИ)
d=$(date +%u); m=$(date +%-m); day=$(date +%-d)
pick() { shift "$1"; echo "$1"; }  # pick N a b c ... -> the Nth word
case "$1" in
    bar)  echo "$(pick "$d" ПН ВТ СР ЧТ ПТ СБ ВС) $day $(pick "$m" ЯНВ ФЕВ МАР АПР МАЙ ИЮН ИЮЛ АВГ СЕН ОКТ НОЯ ДЕК)" ;;
    lock) echo "$(pick "$d" ПОНЕДЕЛЬНИК ВТОРНИК СРЕДА ЧЕТВЕРГ ПЯТНИЦА СУББОТА ВОСКРЕСЕНЬЕ) $day $(pick "$m" ЯНВАРЯ ФЕВРАЛЯ МАРТА АПРЕЛЯ МАЯ ИЮНЯ ИЮЛЯ АВГУСТА СЕНТЯБРЯ ОКТЯБРЯ НОЯБРЯ ДЕКАБРЯ)" ;;
    name)
        n=$(getent passwd "$USER" | cut -d: -f5 | cut -d, -f1); n=${n:-$USER}
        echo "$n" | LC_ALL=C.UTF-8 sed 's/.*/\U&/; s/CH/Ч/g; s/SH/Ш/g; s/LL/Й/g; s/QU/К/g; s/X/КС/g; s/Ñ/НЬ/g; s/Á/А/g; s/É/Е/g; s/Í/И/g; s/Ó/О/g; s/Ú/У/g' |
            LC_ALL=C.UTF-8 sed 'y/ABCDEFGHIJKLMNOPQRSTUVWYZ/АБКДЕФГХИХКЛМНОПКРСТУВВЙЗ/' ;;
esac
