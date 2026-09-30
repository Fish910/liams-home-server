# Kiosk Display

The laptop's own screen shows the dashboard with no desktop environment.

**Packages:** `xserver-xorg x11-xserver-utils xinit openbox chromium-browser unclutter`

**Flow:** autologin on tty1 (getty override) runs `startx` via `~/.bash_profile`, which runs `~/.xinitrc`, which starts Openbox and then Chromium in `--kiosk` mode pointed at `http://localhost:3000`.

**Gotcha:** without a short `sleep 2` between starting Openbox and Chromium, Chromium rendered at half-screen because no window manager was ready.

**Tradeoff:** autologin means physical access equals a shell. SSH still requires normal authentication. This was a deliberate choice.

**Screen toggle:** `scripts/screentoggle.sh` flips DPMS state. Make sure `.bash_profile` sources `.bashrc`, or the alias won't exist in SSH sessions and typing `screen` launches GNU Screen instead.
