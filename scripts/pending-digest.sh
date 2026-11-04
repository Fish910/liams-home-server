#!/bin/bash
# Weekly digest: pending manual updates, auto-update problems, aborted safe reboots.
TOPIC=$(cat ~/.config/ntfy-topic) || exit 1
LOG=~/docker/autoupdate/autoupdate.log
msg=""
pend=$(grep -v '^$' ~/docker/autoupdate/pending 2>/dev/null | tr '\n' ' ')
[ -n "$pend" ] && msg+="Pending manual updates: $pend"$'\n'
prob=$(grep -E 'UNHEALTHY|rolled back|ROLLBACK|pull failed|could not check|buildx' "$LOG" 2>/dev/null | tail -5)
[ -n "$prob" ] && msg+="Auto-update problems:"$'\n'"$prob"$'\n'
ab=$(journalctl -t safe-reboot --since '8 days ago' --no-pager -q 2>/dev/null | tail -2)
[ -n "$ab" ] && msg+="Safe reboot aborted:"$'\n'"$ab"$'\n'
[ -z "$msg" ] && exit 0
prio=low; [ -n "$prob$ab" ] && prio=high
curl -s -m 15 -H "Title: Server weekly digest" -H "Priority: $prio" -H "Tags: package" -d "$msg" "https://ntfy.sh/$TOPIC" >/dev/null
