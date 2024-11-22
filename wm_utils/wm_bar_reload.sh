#!/bin/sh

echo "Reload status bar"
if [ -n "$WAYLAND_DISPLAY" ]; then
    pkill waybar; waybar &
else
    ~/.config/polybar/launch.sh & # Kills previous polybars itself
fi
