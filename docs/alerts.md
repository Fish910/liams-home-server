# Phone Alerts

Living away from the server means nobody is looking at the kiosk, so problems have to come to me. Alerts go to my phone through [ntfy](https://ntfy.sh), a free push service with an iOS/Android app.

## Design

- **Each machine watches the other.** A dead server can't report itself, so the Raspberry Pi watches the server and the server watches the Pi.
- **They reuse the status API.** The service-status API (see [kiosk.md](kiosk.md)) already knows which services are up. The watcher in `scripts/status-alert.py` polls it every minute.
  - **On the Pi:** watches the server and container tiles, and also alerts if the API stops answering for 3 minutes (machine, network, or Tailscale down).
  - **On the server:** watches the Pi tiles (including "unreachable").
- **Debounced.** A tile has to stay bad for 2 polls before an alert fires, and a "Recovered" message follows when it clears. Short container restarts don't page me.
- **Quiet during maintenance.** Alerts are muted Sunday 03:25 to 04:30 (container updates and the weekly reboot). If something is still down at 04:30, the alert fires then.
- **Private topic.** The ntfy topic is a long random string stored in `~/.config/ntfy-topic` (mode 600) on both machines. It is the only secret involved: anyone who knows it can read the alerts, so it is never committed and alerts carry nothing sensitive.

## Other checks

| Script | When | What |
|---|---|---|
| `scripts/pending-digest.sh` | Sundays 09:15 | Pending manual container updates, any auto-update failures or rollbacks, any aborted safe reboots. Silent if there is nothing to report. |
| `scripts/drive-check.sh` | Daily 08:20 | Alerts if `/mnt/storage` is not mounted, the drive's SMART status is not OK, a disk is 90% full, or the kernel logged filesystem or I/O errors in the last 25 hours. Silent when healthy. |

The drive is a USB enclosure whose bridge only answers SMART in generic SCSI mode (`smartctl -d scsi`), which gives a pass/fail health status but no detailed attributes. A narrow sudoers rule (`systemd/smartctl-check.sudoers`) lets the script run exactly that one command without a password.

## Setup

1. Pick a topic and install the ntfy app: `echo "liams-srv-$(openssl rand -hex 8)" > ~/.config/ntfy-topic && chmod 600 ~/.config/ntfy-topic`, then subscribe to it in the app.
2. Copy the scripts to `~/scripts/` and the unit files from `systemd/` (replace the `USER`, `SERVER_LAN_IP` and `SERVER_TAILSCALE_IP` placeholders) to `/etc/systemd/system/`. On the Pi, install `status-alert-pi.service` as `status-alert.service` and copy the same topic file over.
3. `sudo systemctl enable --now status-alert.service pending-digest.timer drive-check.timer`
4. Test: `python3 ~/scripts/status-alert.py --test` and `~/scripts/drive-check.sh --test`. To test the live path, stop a harmless service (`systemctl --user stop midi-pattern`), wait about 3 minutes for the alert, then start it again for the "Recovered" message.

## Related reliability fixes

Because the server is unattended, the Tailscale node keys for the server and Pi have key expiry disabled (otherwise they drop off the tailnet after about 180 days), and the storage drive's `/etc/fstab` entry uses its UUID with `nofail` so a missing drive can't hang boot.
