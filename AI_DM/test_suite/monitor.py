#!/usr/bin/env python3
"""
Standalone service monitor for Project Nexus.
Runs in background, logs health of engine, game, Sail, Anchor every N seconds.

Usage:
  python3 monitor.py              # default 5s interval
  python3 monitor.py --interval 2 # every 2 seconds
  python3 monitor.py --log /path/to/monitor.log
"""

import argparse
import time
import subprocess
from pathlib import Path
from datetime import datetime

def check_services() -> dict:
    snapshot = {"timestamp": datetime.utcnow().isoformat() + "Z", "services": {}}
    # Engine
    r = subprocess.run(["pgrep", "-f", "engine/main.py"], capture_output=True, text=True)
    snapshot["services"]["engine"] = bool(r.stdout.strip())
    # Game
    r1 = subprocess.run(["pgrep", "-f", "soh.appimage"], capture_output=True, text=True)
    r2 = subprocess.run(["pgrep", "-f", "soh"], capture_output=True, text=True)
    pids = set(r1.stdout.split() + r2.stdout.split())
    snapshot["services"]["game"] = len(pids) > 0
    # Sail
    r = subprocess.run(["pgrep", "-f", "sail_server"], capture_output=True, text=True)
    snapshot["services"]["sail"] = bool(r.stdout.strip())
    # Anchor
    r = subprocess.run(["pgrep", "-f", "anchor_server"], capture_output=True, text=True)
    snapshot["services"]["anchor"] = bool(r.stdout.strip())
    # Ports
    ss = subprocess.run(["ss", "-tln"], capture_output=True, text=True).stdout
    snapshot["ports"] = {
        "anchor_43383": ":43383" in ss,
        "sail_43384": ":43384" in ss,
    }
    return snapshot

def format_line(snapshot: dict) -> str:
    svc = snapshot["services"]
    line = f"[{snapshot['timestamp']}] "
    line += f"engine={'✓' if svc['engine'] else '✗'} "
    line += f"game={'✓' if svc['game'] else '✗'} "
    line += f"sail={'✓' if svc['sail'] else '✗'} "
    line += f"anchor={'✓' if svc['anchor'] else '✗'} | "
    line += f"ports: anchor_43383={snapshot['ports']['anchor_43383']} sail_43384={snapshot['ports']['sail_43384']}"
    return line

def main():
    parser = argparse.ArgumentParser(description="Project Nexus Service Monitor")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
    parser.add_argument("--log", type=str, default="/home/donn/HylianModding/AI_DM/monitor.log", help="Log file path")
    args = parser.parse_args()

    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[Monitor] Starting — interval={args.interval}s, log={log_path}")
    print("  Press Ctrl+C to stop\n")

    try:
        while True:
            snap = check_services()
            line = format_line(snapshot=snap)
            print(line)
            with open(log_path, "a") as f:
                f.write(line + "\n")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[Monitor] Stopped")

if __name__ == "__main__":
    main()
