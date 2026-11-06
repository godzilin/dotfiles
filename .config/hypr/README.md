# Hyprland: chuleta y recuperación

## Atajos

| Tecla | Acción |
|---|---|
| Super (soltar) / Super+Espacio / Alt+F1 | Lanzador (fuzzel) |
| Super+º / Super+Enter | Terminal (Alacritty) |
| Super+Tab | Nuevo chat de Claude Code (en `~`) |
| Super+W / D / S / X / C / E | Firefox / Discord / Steam / Lutris / Ajustes KDE / Thunar |
| Super+Q / Alt+F4 | Cerrar ventana |
| Super+Ctrl+Esc | Matar ventana |
| Super+F / Super+Alt+Espacio | Flotar / teselar |
| Super+M / Super+F11 | Maximizar / pantalla completa |
| Super+Mayús+M / Super+Retroceso | "Minimizar" al cajón / mostrar el cajón |
| Super+T | Cambiar dirección del split |
| Super+P | Fijar ventana (visible en todos los escritorios) |
| Super+R, flechas, Esc | Modo redimensionar |
| Super+flechas (o Super+Alt+flechas) | Mover foco |
| Super+Shift+flechas | Mover ventana |
| Super+1..9 / Ctrl+F1..F4 | Ir al escritorio |
| Super+Shift+1..9 | Mandar ventana al escritorio |
| Super+Ctrl+←/→ (+Shift) | Escritorio anterior/siguiente (llevando la ventana) |
| 3 dedos ←/→ | Cambiar de escritorio |
| Super+arrastrar izq/der | Mover / redimensionar con el ratón |
| Alt+Tab | Ciclar ventanas |
| Super+V | Historial del portapapeles |
| Super+N | Centro de notificaciones |
| Super+B | Cambiar perfil de energía |
| Super+L | Bloquear |
| Ctrl+Alt+Supr | Menú de apagado |
| Impr / Shift+Impr | Captura de zona / pantalla completa |
| Super+Shift+B | Reiniciar waybar |
| Super+Alt+W | Siguiente wallpaper (aleatorio) |

## Reglas para que no se rompa

1. Tras editar algo: `Hyprland --verify-config`. Si sale `config ok`, está bien.
2. Solo paquetes de los repos oficiales. Nada de `-git` ni plugins de `hyprpm`.
3. Antes de actualizar: lee las noticias de Hyprland (salen solas tras cada update)
   y fíjate en la versión: `pacman -Qi hyprland | grep Version`.
4. Guarda los cambios: `dots add -u && dots commit -m "..."`.

## Varios equipos

Los temas, atajos y demás se comparten por `main`. Lo propio de cada máquina (monitores, GPU) va en
`hosts/<hostname>.lua`, que `env.lua` carga solo en ese equipo. `dots pull` y `dots push` sincronizan a mano.
El tema activo (`themes/current`) no está en el repo: cada equipo tiene el suyo.

Con `workspace_offsets` en el archivo del host, cada monitor tiene su propio 1..9: en el sobremesa, DP-1 usa los ids 1-9
y HDMI-A-1 los 11-19, que las barras muestran como 1-9 (`format-icons` de cada tema). No renombres esos escritorios ni uses
el mismo nombre en dos monitores: Waybar marca el activo por nombre. Tampoco hagas `persistent-workspaces` en Waybar: los
persistentes van en las reglas de Hyprland.

## Si algo se rompe

- **Barra roja arriba**: error de config. Dice el archivo y la línea.
- **Hyprland no arranca**: en el login elige "Plasma" (KDE sigue intacto),
  arregla la config y comprueba con `Hyprland --verify-config`.
- **Volver a una config que funcionaba**: `dots log`, luego `dots checkout <commit> -- .config/hypr`.
- **Una actualización rompió el sistema**: en el menú de Limine arranca un snapshot
  anterior y restáuralo con btrfs-assistant.
- **Rehacer KDE como estaba**: `konsave -a pre-hyprland`.
