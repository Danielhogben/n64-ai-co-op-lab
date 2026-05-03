#!/bin/bash
# Start the Anchor Server (for Co-Op multiplayer support)
echo "[System] Starting Anchor Co-Op Server..."
cd /home/donn/HylianModding/CoOp/anchor
go build -o anchor_server .
./anchor_server > ~/anchor_server.log 2>&1 &
ANCHOR_PID=$!

# Start the Sail Server (to handle communication with Ship of Harkinian)
echo "[System] Starting Sail Server..."
cd /home/donn/HylianModding/AI_DM
deno run --allow-net --allow-read /home/donn/HylianModding/AI_DM/sail_server.ts > ~/sail_server.log 2>&1 &
SAIL_PID=$!

# Cleanup function to kill background processes on exit
cleanup() {
    echo "[System] Stopping background servers..."
    kill $ANCHOR_PID $SAIL_PID
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for servers to start
sleep 3

# Start the AI DM
echo "[System] Starting AI DM..."
/home/donn/HylianModding/venv/bin/python /home/donn/HylianModding/AI_DM/run_dm.py "$@"

# If DM exits normally, clean up
cleanup
