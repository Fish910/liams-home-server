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
