#!/bin/bash

# CONFIGURE THIS VALUE
IDLE_THRESHOLD_MINUTES=30
CHECK_INTERVAL=60  # seconds

echo "[MONITOR] Watching for inactivity. Will shut down pod after ${IDLE_THRESHOLD_MINUTES} minutes idle."

idle_time=0

while true; do
    # Count active non-system user processes
    active_processes=$(ps -eo pid,etime,comm | grep -vE 'bash|python|grep|ps|sshd|monitor_idle_shutdown' | wc -l)

    if [[ "$active_processes" -gt 1 ]]; then
        echo "[MONITOR] Detected activity. Resetting idle timer."
        idle_time=0
    else
        idle_time=$((idle_time + CHECK_INTERVAL))
        echo "[MONITOR] Idle for $((idle_time / 60)) minute(s)..."
    fi

    if [[ "$idle_time" -ge $((IDLE_THRESHOLD_MINUTES * 60)) ]]; then
        echo "[MONITOR] Idle threshold exceeded. Pausing pod..."
        python3 /root/scripts/runpod_ctl.py pause
        break
    fi

    sleep "$CHECK_INTERVAL"
done