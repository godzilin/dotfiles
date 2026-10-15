#!/bin/sh
# Cycle power profile (Super+B): power-saver -> balanced -> performance
case "$(powerprofilesctl get)" in
    power-saver) next=balanced ;;
    balanced)    next=performance ;;
    *)           next=power-saver ;;
esac
powerprofilesctl set "$next" && notify-send -a power -i battery "Perfil de energía" "$next"
