#!/bin/bash
# Unified Launcher for Project Nexus: Space Universe
SCRIPT_DIR="/home/donn/HylianModding/AI_DM"
SOH_DIR="/home/donn/HylianModding/ShipOfHarkinian"
SOH_APPIMAGE="$SOH_DIR/soh.appimage"

echo "============================================================"
echo "🚀 PROJECT NEXUS: SPACE UNIVERSE"
echo "   AI Full Universe Mod — 362 ROMs | 8 Galaxies | 64 Zones"
echo "============================================================"

# 1. Start the Universe Engine in the background
echo "[Launcher] Starting AI DM Engine in background..."
echo "--- Engine Start: $(date) ---" > "$SCRIPT_DIR/engine.log"
(cd "$SCRIPT_DIR" && nohup python3 -u engine/main.py >> engine.log 2>&1 </dev/null) &
ENGINE_PID=$!
sleep 2
if ps -p $ENGINE_PID > /dev/null 2>&1; then
    echo "[Launcher] Engine running (PID: $ENGINE_PID)"
else
    echo "⚠️  Warning: Engine may have failed to start. Check engine.log"
fi

# 2. Start Ship of Harkinian with the full universe mod
echo "[Launcher] Starting Ship of Harkinian..."
if [ -f "$SOH_APPIMAGE" ]; then
    cd "$SOH_DIR"
    # Launch SoH with mods enabled
    ./soh.appimage
else
    echo "❌ Error: soh.appimage not found at $SOH_APPIMAGE"
    kill $ENGINE_PID 2>/dev/null
    exit 1
fi

echo "[Launcher] Game exited. Shutting down engine..."
kill $ENGINE_PID 2>/dev/null
echo "✅ Done."
