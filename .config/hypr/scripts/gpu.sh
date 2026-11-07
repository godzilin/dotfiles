#!/bin/sh
# Modulo custom/gpu de waybar: uso y temperatura de la NVIDIA cada 2 s; VRAM y consumo en el tooltip
nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total,power.draw \
    --format=csv,noheader,nounits -l 2 |
while IFS=', ' read -r use temp mem total power; do
    printf '{"text":"GPU %s%% %s°C","tooltip":"VRAM %s de %s MiB · %s W"}\n' "$use" "$temp" "$mem" "$total" "$power"
done
