#!/bin/bash
NEWEST=$(ls /boot/vmlinuz-* | sed 's|/boot/vmlinuz-||' | sort -V | tail -1)
if ! modinfo -k "$NEWEST" nvidia >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y "linux-modules-nvidia-595-open-$NEWEST"
fi
if ! modinfo -k "$NEWEST" nvidia >/dev/null 2>&1; then
  logger -t safe-reboot "NVIDIA module missing for $NEWEST - reboot aborted"
  exit 1
fi
/sbin/reboot
