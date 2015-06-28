#!/usr/bin/env bash
pids="$(ps aux | grep bot.py | grep -v grep | awk '{print $2}')"
for pid in $pids; do
    kill -TERM $pid && echo "$pid killed"
done
