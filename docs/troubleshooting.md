# Troubleshooting: Why Tool Calls Weren't Working

Custom tools appeared enabled but the model never called them. Two separate bugs were compounding.

## How I isolated it
I bypassed Open WebUI and sent a hand-built `tools` array straight to Ollama's `/api/chat` with `curl`. It worked, which proved the model and Ollama were fine and the problem was in the UI layer. That saved me from swapping models unnecessarily.

## Bug 1: Builtin Tools override custom tools
With Open WebUI's "Builtin Tools" capability enabled, custom Python tools were silently replaced: the model only ever saw the builtin set. **Fix:** disable Builtin Tools in the model's Capabilities (Workspace, Models, Capabilities).

## Bug 2: Stale bind mount
Reads of `/mnt/ai-storage` failed with `Errno 5` (I/O error). `dmesg` showed the external drive had disconnected and reconnected, leaving the container with a stale mount. **Fix:** `docker compose down && docker compose up -d`.

## Lesson
Check the Builtin Tools setting and mount freshness before blaming the model or the function-calling mode.

## Smaller gotchas
- Homepage `metric:` fields belong in `services.yaml` tiles, not `widgets.yaml`. Mixing them fails silently.
- Each `glances` widget renders CPU+RAM unless `cpu: false` / `mem: false`.
- Accessing Homepage by IP requires `HOMEPAGE_ALLOWED_HOSTS`.
- Glances' `containers` metric is broken with Homepage (upstream API mismatch); use Homepage's native Docker integration instead.

# Troubleshooting: Services Broken After the Scheduled Reboot

Everything worked after a manual shutdown and power-on, but the Sunday reboot left Ollama and other services broken.

## Cause 1: kernel without its NVIDIA module
An unattended upgrade installed a new kernel but kept back the matching `linux-modules-nvidia-*` package. After the reboot the GPU driver wasn't loaded, so the Docker NVIDIA runtime failed and Ollama never started. **Fix:** `scripts/safe-weekly-reboot.sh` checks the newest kernel for an NVIDIA module and installs it (or aborts) before rebooting.

## Cause 2: `Persistent=true` on the reboot timer
A missed run fired as soon as the machine next booted, causing a reboot during startup. **Fix:** `Persistent=false`.

## A wrong theory worth recording
I first suspected the external drive's USB power. Reading the boot log (`modinfo`, `nvidia-smi`, `docker` errors) showed the real cause. Verify before blaming hardware.

# Troubleshooting: Inconsistent MIDI Keyboard Audio

The FluidSynth service sometimes had no sound. The log said `Failed to open the "hw:1,0" audio device`. ALSA card numbers depend on enumeration order, so the USB MIDI interface was card 1 on some boots and card 0 on others. **Fix:** address the card by name (`hw:PCH,0`) instead of number. Lesson: never hard-code ALSA card numbers.

# Troubleshooting: Tailscale Shows Idle Devices as Offline

The `Active` field is false for devices with no recent traffic, so idle phones and the Pi looked offline. `docker/tailscale-status/status.py` now refreshes in a background thread every 90 seconds and sends a single `tailscale ping` only to peers that aren't `Active`. The web handler returns the cached result, so page loads cost nothing.

# Troubleshooting: Homepage Layout Gotchas

- **CSS rules ignored:** Homepage's layout nests each tile list inside a collapsible panel that stays `display: block`. Stretching columns to equal heights needed JS inline styles with `!important` (see `docs/kiosk.md`).
- **Headless Chromium diagnostics:** measuring the page with `--dump-dom` works with a plain `setTimeout`; waiting for the `load` event returned nothing.
- **Inline `!important` beats stylesheet `!important`-less rules, and flex direction set that way can't be changed from CSS.** Position elements absolutely instead.
- **`customapi` widgets:** max 4 fields each, and values can't be coloured natively. Colour by tagging blocks from JS.
