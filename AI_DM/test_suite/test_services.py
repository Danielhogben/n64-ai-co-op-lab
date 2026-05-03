import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime

# Test suite imports
from helpers import assert_true
from engine_connector import EngineConnector

class ServiceMonitor:
    """Background monitor that logs service health every N seconds."""

    def __init__(self, interval: int = 5, log_path: str = None):
        self.interval = interval
        self.log_path = Path(log_path or "/home/donn/HylianModding/AI_DM/monitor.log")
        self._stop = threading.Event()
        self._thread = None

    def _check(self) -> dict:
        """Return health snapshot of all services."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {}
        }
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

    def _log(self, snapshot: dict):
        entry = f"[{snapshot['timestamp']}] "
        svc = snapshot["services"]
        entry += f"engine={'✓' if svc['engine'] else '✗'} game={'✓' if svc['game'] else '✗'} sail={'✓' if svc['sail'] else '✗'} anchor={'✓' if svc['anchor'] else '✗'} | ports: anchor_43383={snapshot['ports']['anchor_43383']} sail_43384={snapshot['ports']['sail_43384']}"
        with open(self.log_path, "a") as f:
            f.write(entry + "\n")

    def _loop(self):
        while not self._stop.is_set():
            snap = self._check()
            self._log(snap)
            time.sleep(self.interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[Monitor] Started (interval={self.interval}s, log={self.log_path})")

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        print("[Monitor] Stopped")

# Auto-start when imported if environment variable set
import os
if os.environ.get("NEXUS_MONITOR_AUTOSTART"):
    mon = ServiceMonitor()
    mon.start()

def ensure_game_running(timeout: int = 15) -> bool:
    """Start the game via launcher if not already running."""
    import time
    ec = EngineConnector()
    if ec.is_game_running():
        return True
    print("[*] Game not running — launching via play_game.sh...")
    launcher = Path("/home/donn/HylianModding/AI_DM/play_game.sh")
    if not launcher.exists():
        print("  ⚠ Launcher not found")
        return False
    # Launch in background
    subprocess.Popen(
        ['bash', str(launcher)],
        cwd=str(launcher.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    # Wait for game process to appear
    start = time.time()
    while time.time() - start < timeout:
        if EngineConnector.is_game_running():
            print("  ✓ Game started")
            return True
        time.sleep(0.5)
    print("  ✗ Game did not start within timeout")
    return False

def run():
    import time
    print("\n" + "="*60)
    print("PHASE 1: SERVICE HEALTH & CONNECTIVITY")
    print("="*60 + "\n")

    ec = EngineConnector()
    passed = 0; total = 0

    print("[1.1] Process existence checks:")
    checks = [
        (ec.is_engine_running, "AI DM engine process running"),
        (ec.is_game_running,   "Ship of Harkinian running"),
        (ec.is_sail_running,   "Sail server running"),
        (ec.is_anchor_running, "Anchor relay running"),
    ]
    for fn, msg in checks:
        total += 1
        if assert_true(fn(), msg):
            passed += 1

    # If game wasn't running, try to start it now and re-check
    if not ec.is_game_running():
        if ensure_game_running(12):
            total += 1
            if assert_true(ec.is_game_running(), "Game launched successfully"):
                passed += 1
        else:
            # Still failed — count as fail
            total += 1
            if assert_true(False, "Game failed to launch"):
                passed += 1

    print("\n[1.2] Port binding checks:")
    result = subprocess.run(['ss', '-tln'], capture_output=True, text=True)
    total += 1
    if assert_true(':43383' in result.stdout, "Anchor port 43383 listening"):
        passed += 1
    total += 1
    if assert_true(':43384' in result.stdout, "Sail port 43384 listening"):
        passed += 1

    print("\n[1.3] Engine log sanity:")
    total += 1
    log = ec.log_path
    if assert_true(log.exists() and log.stat().st_size > 0, "Engine log exists and non-empty"):
        passed += 1
    total += 1
    tail = ec.tail_log(200)
    if assert_true("ENGINE READY" in tail or "Engine ready" in tail,
                   "Engine reports ready in log"):
        passed += 1

    print(f"\n[1.x] Phase 1 summary: {passed}/{total} passed")
    return passed, total
