# Home Server

An old Acer Nitro 5 gaming laptop repurposed as an always-on home server: network file storage, a live monitoring dashboard on its own screen, and a GPU-accelerated local LLM stack with custom tools that let the model safely read and write files.

![Kiosk dashboard](images/kiosk-dashboard.jpg)
<!-- Replace with your best photo of the dashboard running on the laptop screen -->

## What it does

- **File storage:** Samba share on an external ext4 drive, reachable on the LAN and remotely over Tailscale
- **Dashboard:** Homepage running fullscreen in kiosk mode on the server's own display
- **Local AI:** Ollama + Open WebUI with GPU passthrough on a 4 GB GTX 1650
- **Custom AI tools:** sandboxed file and image tools the model can call
- **Monitoring:** Glances feeding CPU, RAM, GPU, disk, and network widgets

## Hardware

| Part | Spec |
|---|---|
| Machine | Acer Nitro 5 |
| CPU | Intel Core i5-9300H |
| GPU | NVIDIA GTX 1650, 4 GB VRAM (the ceiling for model size) |
| RAM | 16 GB |
| Internal storage | 235 GB NVMe (LVM) |
| External storage | Seagate BUP Slim, ext4, mounted at `/mnt/storage` |
| OS | Ubuntu 26.04 LTS |

## Architecture

![Architecture](images/architecture.svg)

| Service | Runs as | Port | Purpose |
|---|---|---|---|
| Homepage | Docker | 3000 | Dashboard |
| Glances | Host (pipx) | 61208 | Metrics API for Homepage widgets |
| Ollama | Docker | 11434 | LLM inference (GPU) |
| Open WebUI | Docker | 3001 | Chat UI and tool host |
| Tailscale status API | Docker | 5005 | Custom device online/offline endpoint |
| Samba, Tailscale | Host | n/a | Need direct host network/filesystem access |

## Design decisions

- **Samba and Tailscale run on the host, not in containers.** Both need direct access to the host network stack and filesystem; Docker networking adds complexity with no benefit here.
- **AI tools are sandboxed.** The model can read anywhere under the storage share but can only write inside one `sandbox/` folder, with path-traversal protection. `docker.sock` is never mounted into a container the model can reach, and SSH keys are excluded from every read scope.
- **Ollama is never exposed publicly.**

## Write-ups

- [Hardware and storage](docs/hardware.md): including the LVM fix that recovered 130 GB
- [Networking](docs/networking.md)
- [Kiosk display](docs/kiosk.md)
- [Local AI stack](docs/ai-setup.md)
- [Troubleshooting: the tool-calling bug hunt](docs/troubleshooting.md)

## Repo layout

```
docker/            compose files for each service
openwebui-tools/   custom Python tools for Open WebUI
scripts/           helper scripts (screen toggle, scheduled shutdown)
docs/              detailed write-ups
images/            photos and diagrams
```

## Roadmap

- [ ] Vision model (moondream) for image understanding
- [ ] Voice assistant pipeline: wake word, Whisper, Ollama, Piper
- [ ] Raspberry Pi as an always-on relay for scheduling and remote wake
- [ ] Automated config backups

## Notes

IPs, hostnames, and tailnet names in this repo are placeholders (`<lan-ip>`, `<tailscale-ip>`). Adjust for your own setup.
