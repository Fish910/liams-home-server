#!/usr/bin/env python3
import json, subprocess, threading, time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

INTERVAL = 90
KEYS = ("phone", "laptop", "pi", "ipad")
cache = {k: "Offline" for k in KEYS}
cache["total_online"] = 0
lock = threading.Lock()

def classify(peer):
    dns = peer.get("DNSName", "").lower()
    host = peer.get("HostName", "")
    if "iphone" in dns: return "phone"
    if "ipad" in dns: return "ipad"
    if host == "your-laptop": return "laptop"
    if host == "pi-host": return "pi"
    return None

def reachable(peer):
    if peer.get("Active"):
        return True
    ips = peer.get("TailscaleIPs") or []
    if not ips:
        return False
    try:
        r = subprocess.run(
            ["tailscale", "ping", "--c=1", "--until-direct=false", "--timeout=4s", ips[0]],
            capture_output=True, text=True, timeout=8)
        return "pong from" in r.stdout
    except Exception:
        return False

def refresh_loop():
    while True:
        try:
            raw = subprocess.run(["tailscale", "status", "--json"],
                                 capture_output=True, text=True, check=True, timeout=10).stdout
            peers = [(classify(p), p) for p in json.loads(raw).get("Peer", {}).values()]
            peers = [(k, p) for k, p in peers if k]
            with ThreadPoolExecutor(max_workers=4) as ex:
                results = list(ex.map(lambda kp: reachable(kp[1]), peers))
            out = {k: "Offline" for k in KEYS}
            for (k, _), ok in zip(peers, results):
                out[k] = "Online" if ok else "Offline"
            out["total_online"] = sum(results)
            with lock:
                cache.update(out)
        except Exception as e:
            print("refresh failed:", e, flush=True)
        time.sleep(INTERVAL)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_response(404); self.end_headers(); return
        with lock:
            body = json.dumps(cache).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass

threading.Thread(target=refresh_loop, daemon=True).start()
ThreadingHTTPServer(("0.0.0.0", 5005), Handler).serve_forever()
