# Home Assistant Integrations

Home Assistant runs in Docker with host networking and is reachable over HTTPS via Tailscale Serve. Config layout: `configuration.yaml` holds `rest_command`, `template`, `input_boolean`, and `input_number` blocks; `automations.yaml` and `scripts.yaml` are included files. The default dashboard is a YAML-mode dashboard with sections for bedroom lights, ceiling LEDs, desk LEDs, display LEDs, fan, music, and the server.

## The Flask bridge pattern
Hardware that Home Assistant can't reach natively is wrapped in a small Flask API on whichever machine it's physically attached to. HA calls it with `rest_command`, and the responses (JSON) are parsed automatically into dicts. APIs exist for:

| API | Host | Purpose |
|---|---|---|
| LED (IR) | Pi | Send IR codes with a repeat count |
| Fan (RF) | Pi | Talk to the Arduino over serial |
| Screen | Server | Turn the kiosk display on/off |
| Camera | Server | Persistent ffmpeg grabbing a frame at 2 fps |
| Color extract | Server | Dominant color of the current album art |

Each runs as a systemd service.

## RF fan and light
Arduino Uno + CC1101 (315 MHz), sketch compiled and uploaded directly on the Pi with `arduino-cli`. Exposed as template `fan` and `light` entities.

## IR LED strips
Pi GPIO drives the IR LED; codes are sent with a per-strip repeat count through a `send_ir_code` command using a Jinja default for `repeats`.

## Bluetooth LED strip
`elkbledom` integration, with an automation every 20 seconds as a keepalive. A second automation extracts the dominant color from the current album art and applies it, but only when the light is already on.

## MIDI chords
MIDI keyboard into the laptop. FluidSynth (user systemd service) plays it; a pattern service detects chords and melodies and calls the Home Assistant API on a background worker thread so the keyboard never lags.

## Music
Music Assistant feeds a Snapcast client on the Pi, which outputs to a Bluetooth speaker via BlueALSA. PipeWire is masked system-wide because it claims the A2DP transport before BlueALSA can.

## Voice
Echo Dot (rooted, EchoMuse) to Wyoming Whisper to Ollama (Home Assistant conversation agent) to Wyoming Piper. Sentence-trigger automations handle frequent commands without the LLM.

## Gotchas worth knowing
- Appending a duplicate top-level key to `configuration.yaml` silently replaces the existing block. Merge instead.
- New `rest_command` entries need a container restart; automations reload live.
- Always run `check_config` before restarting.
- An `ffmpeg` camera with an RTSP source makes HA dashboards retry a stream forever. A `generic` still-image camera avoids it.
- `sudo >>` fails because the redirect is opened before sudo applies; use `sudo tee -a`.
- A systemd unit with both `After=graphical.target` and `WantedBy=multi-user.target` creates a cycle that silently drops the job at boot.
