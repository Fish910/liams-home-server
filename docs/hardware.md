# Hardware and Storage

## Why this machine
A retired gaming laptop has a built-in battery (a free UPS), a built-in screen (a free dashboard display), and a discrete GPU, which a Pi or mini-PC would not offer.

## Fixing the "missing" 130 GB
The 235 GB NVMe showed only ~105 GB usable. The installer had under-provisioned the LVM logical volume. Fix:

```bash
sudo lvextend -l +100%FREE /dev/<vg>/<lv>
sudo resize2fs /dev/<vg>/<lv>
```

## External storage
A Seagate BUP Slim was reformatted to ext4 and mounted at `/mnt/storage`, which is the Samba share location. Persistence across reboots is via `/etc/fstab` (use the drive's UUID, not `/dev/sdX`).

## Power scheduling
`rtcwake` works on this hardware (tested with a 60-second wake). Caveat: waking from full power-off likely requires AC power. A manual `sleepnow` command shuts down immediately and schedules a 9:00 AM wake. See `scripts/`.
