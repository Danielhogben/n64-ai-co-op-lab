#!/bin/bash
# Launcher for Project Nexus: Space Universe
# This starts the engine main loop and the interactive console concurrently.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Project Nexus Engine..."
python3 engine/main.py "$@"
