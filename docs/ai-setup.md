# Local AI Stack

## Models (sized for 4 GB VRAM)
`llama3.2:3b`, `mistral:7b`, `qwen3:4b`. `phi3:mini` was tried and does not support tool calling.

## GPU passthrough
`nvidia-container-toolkit` plus a `deploy.resources.reservations.devices` block in the Ollama compose file. Verified with `nvidia-smi` showing utilization during generation.

## Custom tools (Open WebUI)
- **Storage tool:** list/read anywhere under the share; write only in `sandbox/`
- **Image tool:** metadata and simple drawing operations (Pillow); writes only in `sandbox/`

Every path passes through a `_resolve_safe()` helper that blocks `../` escapes.

## Security boundaries
- Read-only mount of the share, with a separate read-write mount for the sandbox only
- Never mount `docker.sock` into a model-accessible container
- Exclude `.ssh` from all read scopes
- Ollama's port is never exposed publicly

## Thinking mode
`qwen3:4b` can spend 1-2 minutes reasoning on trivial tool calls. `/no_think` in the system prompt turns it off.
