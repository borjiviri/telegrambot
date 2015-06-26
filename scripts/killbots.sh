#!/usr/bin/env bash
pids="$(ps aux | grep bot.py | grep -v grep | awk '{print $2}')"
for pid in $pids; do
    kill -9 $pid && echo "$pid killed"
done
test -f /tmp/*bot.pid && rm /tmp/*bot.pid
