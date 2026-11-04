#!/usr/bin/env python3
import json, os, re, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 5099
INTERVAL = 30
PER_ROW = 4
PI_HOST = "pi-host"
PI_KEY = os.path.expanduser("~/.ssh/id_status")
ENV = {**os.environ, "XDG_RUNTIME_DIR": "/run/user/1000"}

# group -> (title, icon, [(tile label, kind, [units])]); kind: sys | user | docker | pi
GROUPS = {
    "server": ("Server Services", "mdi-server", [
        ("Piano", "user", ["midi-piano"]),
        ("Patterns", "user", ["midi-pattern"]),
        ("Screen", "sys", ["screen-api"]),
        ("Camera", "sys", ["cam-stream-api"]),
        ("Colors", "sys", ["color-extract"]),
        ("TS Status", "sys", ["tailscale-status"]),
        ("Core", "sys", ["docker", "ssh", "smbd", "tailscaled", "bluetooth",
                         "glances", "chrony", "nvidia-persistenced"]),
    ]),
    "containers": ("Containers", "mdi-docker", [
        ("Home Asst", "docker", ["homeassistant"]),
        ("Music Asst", "docker", ["music-assistant-server"]),
        ("Echomuse", "docker", ["echomuse-controller"]),
        ("Vaultwarden", "docker", ["vaultwarden"]),
        ("Ollama", "docker", ["ollama"]),
        ("Open WebUI", "docker", ["open-webui"]),
        ("Voice", "docker", ["wyoming-whisper", "wyoming-piper", "oww-forge-ui"]),
        ("Homepage", "docker", ["homepage"]),
    ]),
    "pi": ("Raspberry Pi", "mdi-raspberry-pi", [
        ("BT Audio", "pi", ["bluealsa", "bluealsa-aplay"]),
        ("Fan", "pi", ["fan-api"]),
        ("LEDs", "pi", ["pi-led-api"]),
        ("Core", "pi", ["bluetooth", "glances", "tailscaled", "ssh"]),
    ]),
}

def key(g, label):
    return g + "_" + re.sub(r"\W+", "_", label.lower())

def run(cmd, timeout=10):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=ENV).stdout
    except Exception:
        return ""

def sysd(units, user=False):
    if not units: return {}
    cmd = ["systemctl"] + (["--user"] if user else []) + ["is-active"] + units
    return dict(zip(units, run(cmd).split()))

def pi_states(units):
    out = run(["ssh", "-i", PI_KEY, "-o", "BatchMode=yes", "-o", "ConnectTimeout=4",
               "-o", "StrictHostKeyChecking=accept-new", PI_HOST,
               "systemctl is-active " + " ".join(units)], timeout=10).split()
    return dict(zip(units, out)) if out else None

def docker_states():
    d = {}
    for line in run(["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}"]).splitlines():
        name, _, status = line.partition("|")
        d[name] = "WARN" if "unhealthy" in status else ("UP" if status.startswith("Up") else "DOWN")
    return d

def norm(s):
    return {"active": "UP", "UP": "UP", "activating": "START", "WARN": "WARN"}.get(s, "DOWN")

def collect():
    want = {"sys": set(), "user": set(), "pi": set()}
    for _, _, tiles in GROUPS.values():
        for _, kind, units in tiles:
            if kind in want: want[kind].update(units)
    states = {"sys": sysd(sorted(want["sys"])),
              "user": sysd(sorted(want["user"]), user=True),
              "docker": docker_states(),
              "pi": pi_states(sorted(want["pi"]))}
    res = {}
    for g, (_, _, tiles) in GROUPS.items():
        for label, kind, units in tiles:
            st = states[kind]
            if st is None:
                res[key(g, label)] = "UNREACH"; continue
            bad = [(u, norm(st.get(u))) for u in units if norm(st.get(u)) != "UP"]
            if not bad: res[key(g, label)] = "UP"
            elif len(units) == 1: res[key(g, label)] = bad[0][1]
            else: res[key(g, label)] = "DOWN: " + ", ".join(u for u, _ in bad)
    res["updated"] = time.strftime("%H:%M:%S")
    return res

cache, lock = {}, threading.Lock()

def loop():
    while True:
        try:
            r = collect()
            with lock: cache.update(r)
        except Exception as e:
            print("collect failed:", e, flush=True)
        time.sleep(INTERVAL)

def yaml_out():
    for g, (title, icon, tiles) in GROUPS.items():
        print(f"    - {title}:\n        icon: {icon}\n        widgets:")
        for i in range(0, len(tiles), PER_ROW):
            print(f"          - type: customapi\n            url: http://SERVER_IP:{PORT}/status")
            print("            refreshInterval: 30000\n            mappings:")
            for label, _, _ in tiles[i:i + PER_ROW]:
                print(f"              - field: {key(g, label)}\n                label: {label}")
        print()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_response(404); self.end_headers(); return
        with lock: body = json.dumps(cache).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass

if __name__ == "__main__":
    if "--yaml" in sys.argv:
        yaml_out(); sys.exit()
    cache.update(collect())
    threading.Thread(target=loop, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
