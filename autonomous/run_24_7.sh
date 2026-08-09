#!/bin/bash
# Run master automation 24/7

cd /data/data/com.termux/files/home/.pi/skills/antidetect-stack

while true; do
    python3 autonomous/master_automation.py 2>&1
    echo "Sleeping 1 hour..."
    sleep 3600
done
