#!/bin/bash
# Start Universe Engine daemon (background service)
cd /home/donn/HylianModding/AI_DM
nohup python3 -u engine/main.py >> engine.log 2>&1 </dev/null &
echo $! > /tmp/engine.pid
echo "Engine started (PID: $(cat /tmp/engine.pid))"
