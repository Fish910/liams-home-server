#!/usr/bin/env python3
"""Poll the service-status API and push phone alerts through ntfy.

One copy runs on the Pi (watches the server's tiles + whether the server answers)
and one on the server (watches the Pi's tiles), so each watches the other.
"""
import datetime, json, os, sys, time, urllib.request

URLS = [u for u in os.environ.get(
    "ALERT_URLS", "http://127.0.0.1:5099/status").split(",") if u]
PREFIXES = tuple(os.environ.get("ALERT_PREFIXES", "server_,containers_").split(","))
REACH_NAME = os.environ.get("ALERT_REACH_NAME", "")        # empty = don't alert on unreachable
TOPIC_FILE = os.path.expanduser(os.environ.get("NTFY_TOPIC_FILE", "~/.config/ntfy-topic"))
DRYRUN = os.environ.get("ALERT_DRYRUN") == "1"
INTERVAL = int(os.environ.get("ALERT_INTERVAL", "60"))
CONFIRM = 2          # polls a tile must stay bad before alerting
REACH_CONFIRM = 3    # polls with no answer before alerting

def notify(title, body, prio="default", tags=""):
    if DRYRUN:
        print("NOTIFY [%s] %s | %s" % (prio, title, body), flush=True); return
    try:
        topic = open(TOPIC_FILE).read().strip()
        req = urllib.request.Request("https://ntfy.sh/" + topic, data=body.encode(),
                                     headers={"Title": title, "Priority": prio, "Tags": tags})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print("notify failed:", e, flush=True)

def fetch():
    for u in URLS:
        try:
            with urllib.request.urlopen(u, timeout=5) as r:
                return json.load(r)
        except Exception:
            pass
    return None

def pretty(key):
    for p in PREFIXES:
        if key.startswith(p): key = key[len(p):]
    return key.replace("_", " ").title()

def in_maintenance():
    """Sunday 03:25-04:30: container updates and the weekly reboot."""
    n = datetime.datetime.now()
    return n.weekday() == 6 and (n.hour, n.minute) >= (3, 25) and (n.hour, n.minute) <= (4, 30)

def main():
    if "--test" in sys.argv:
        notify("Test alert", "Alerts from %s are working." % os.uname().nodename, "default", "white_check_mark"); return
    bad_count, alerted = {}, {}
    miss, down_alerted = 0, False
    while True:
        data = fetch()
        quiet = in_maintenance()
        if data is None:
            miss += 1
            if REACH_NAME and miss >= REACH_CONFIRM and not down_alerted and not quiet:
                notify("%s not answering" % REACH_NAME,
                       "The status API has not answered for %d minutes. The machine, its network, or Tailscale may be down." % miss,
                       "urgent", "rotating_light"); down_alerted = True
        else:
            if down_alerted:
                notify("%s is back" % REACH_NAME, "Status API is answering again.", "default", "white_check_mark")
            miss, down_alerted = 0, False
            tiles = {k: v for k, v in data.items() if k.startswith(PREFIXES)}
            for k, v in tiles.items():
                bad_count[k] = bad_count.get(k, 0) + 1 if v != "UP" else 0
            new = [k for k, v in tiles.items() if v != "UP" and bad_count[k] >= CONFIRM and k not in alerted]
            back = [k for k in list(alerted) if tiles.get(k) == "UP"]
            if new and not quiet:
                for k in new: alerted[k] = tiles[k]
                notify("%d service(s) down" % len(new),
                       "\n".join("%s: %s" % (pretty(k), tiles[k]) for k in new), "high", "warning")
            if back:
                for k in back: alerted.pop(k)
                notify("Recovered", ", ".join(pretty(k) for k in back), "default", "white_check_mark")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
