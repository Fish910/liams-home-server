# Maintenance: Updates, Reboots, and Power

## Weekly schedule (Sunday)

| Time | What | Where |
|---|---|---|
| 03:00 | Vaultwarden backup | existing job |
| 03:30 | Container update check and auto-update | `systemd/docker-autoupdate.timer` |
| 04:00 | Safe reboot | `systemd/weekly-reboot.timer` |

Both timers use `Persistent=false`. With `Persistent=true`, a missed run (server off at the time) fired immediately on the next boot and rebooted the machine mid-startup.

## Safe reboot

`scripts/safe-weekly-reboot.sh` finds the newest installed kernel and checks that it has an NVIDIA module (`modinfo -k <kernel> nvidia`). If not, it installs `linux-modules-nvidia-<ver>-open-<kernel>`; if that still fails it logs to the journal (`logger -t safe-reboot`) and refuses to reboot. See the troubleshooting write-up for why.

## Container auto-updates

`scripts/docker-autoupdate` compares each image's registry digest with the local one (`docker buildx imagetools inspect`), so checking downloads nothing. Default mode only reports; `--apply` updates.

| Tier | Stacks | Behaviour |
|---|---|---|
| Auto | homepage, vaultwarden, wyoming-piper, wyoming-whisper | Pulled, recreated, health-checked for up to 2 minutes, rolled back (old image re-tagged) if unhealthy |
| Check only | homeassistant, music-assistant, ollama, openwebui | Listed in `autoupdate/pending`, never touched automatically |
| Local builds | echomuse controller, oww-forge | Rebuilt by hand with `docker compose build --pull` |

Home Assistant, Music Assistant and Ollama are check-only because automations and the voice assistant depend on them. Open WebUI follows the rolling `:main` tag, so it is treated the same way. The script runs as a normal user, so no `docker.sock` is exposed to any container.

## Power

`rtcwake` works on this hardware. Waking from full power-off likely needs AC power. The `sleepnow` command shuts down immediately and schedules a 09:00 wake the next day.

Alerts for failed updates, pending updates, and drive health are covered in [alerts.md](alerts.md).
