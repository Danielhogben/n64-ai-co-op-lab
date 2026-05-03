#!/bin/bash
# Start AI Dungeon Master daemon (persistent service)
cd /home/donn/HylianModding/AI_DM
nohup python3 -u run_dm.py >> dm.log 2>&1 </dev/null &
echo $! > /tmp/dm.pid
echo "DM Daemon started (PID: $(cat /tmp/dm.pid))"
