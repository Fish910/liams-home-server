#!/bin/bash
# Daily check of the storage drive. Silent unless something looks wrong (or --test).
TOPIC=$(cat ~/.config/ntfy-topic) || exit 1
msg=""
if ! findmnt -rn /mnt/storage >/dev/null; then
  msg+="/mnt/storage is NOT mounted (drive missing?)"$'\n'
else
  src=$(findmnt -rn -o SOURCE /mnt/storage)
  dev=/dev/$(lsblk -no pkname "$src" | head -1)
  h=$(sudo -n /usr/sbin/smartctl -H -d scsi "$dev" 2>&1 | grep -i 'health status')
  case "$h" in
    *OK*) ;;
    "")   msg+="SMART check could not run on $dev"$'\n' ;;
    *)    msg+="Drive health: $h"$'\n' ;;
  esac
  use=$(df --output=pcent /mnt/storage | tail -1 | tr -dc '0-9')
  [ "${use:-0}" -ge 90 ] && msg+="/mnt/storage is ${use}% full"$'\n'
fi
rootuse=$(df --output=pcent / | tail -1 | tr -dc '0-9')
[ "${rootuse:-0}" -ge 90 ] && msg+="Root disk is ${rootuse}% full"$'\n'
errs=$(journalctl -k --since '25 hours ago' --no-pager -q 2>/dev/null | grep -E 'EXT4-fs error|Buffer I/O error|I/O error, dev sd' | tail -3)
[ -n "$errs" ] && msg+="Disk errors in kernel log:"$'\n'"$errs"$'\n'
[ "$1" = "--test" ] && msg+="Test run: drive check completed (SMART: ${h:-n/a})"$'\n'
[ -z "$msg" ] && exit 0
curl -s -m 15 -H "Title: Server drive check" -H "Priority: high" -H "Tags: warning" -d "$msg" "https://ntfy.sh/$TOPIC" >/dev/null
