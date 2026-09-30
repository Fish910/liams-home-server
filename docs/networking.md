# Networking

- **Samba** exports `/mnt/storage`. Setting `unix extensions = no` in `smb.conf` fixed iOS/macOS clients mounting the share read-only.
- **Tailscale** provides remote access from phone and laptop without opening any router ports.
- **Wake-on-LAN** does not work over Tailscale, because magic packets are local broadcasts. A Raspberry Pi on the LAN is the planned relay.
- A small Python service (`docker/tailscale-status`) exposes device status to the dashboard. It uses the `Active` field rather than `Online`, since `Online` is nearly always true.

Both Samba and Tailscale run directly on the host by design.
