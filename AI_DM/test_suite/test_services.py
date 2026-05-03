import socket
import subprocess
from pathlib import Path
from helpers import assert_true
from engine_connector import EngineConnector

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
