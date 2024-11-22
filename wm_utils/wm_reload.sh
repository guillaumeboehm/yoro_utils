#!/bin/sh

echo "Reload window manager"
if [ -n "$WAYLAND_DISPLAY" ]; then
    hyprctl reload
else
    echo "Reload bspwm ?"
fi
