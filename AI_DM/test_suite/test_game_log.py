from pathlib import Path
from helpers import assert_true
import subprocess

def run():
    print("\n" + "="*60)
    print("PHASE 7: CLIENT & GAME LOG ANALYSIS")
    print("="*60 + "\n")

    log = Path("/home/donn/HylianModding/ShipOfHarkinian/logs/Ship of Harkinian.log")
    passed = 0; total = 0

    print("[7.1] Game log file:")
    total += 1
    if assert_true(log.exists() and log.stat().st_size > 0,
                   "Log exists and non-empty"):
        passed += 1

    tail = subprocess.run(['tail', '-20', str(log)],
                          capture_output=True, text=True).stdout
    print("\n  Last 20 lines:")
    for line in tail.split('\\n')[:20]:
        if line.strip():
            print(f"    {line[:120]}")

    print("\n[7.2] Error scanning (last 2000 chars):")
    snippet = tail if len(tail) < 2000 else tail[-2000:]
    total += 1
    if assert_true("error" not in snippet.lower() and "exception" not in snippet.lower(),
                   "No errors in recent log"):
        passed += 1

    print("\n[7.3] Mod loading confirmation:")
    content = log.read_text() if log.exists() else ""
    total += 1
    if assert_true("ArchiveManager" in content and "Adding Archive" in content,
                   "ArchiveManager processing mods"):
        passed += 1
    total += 1
    if assert_true("oot_reloaded" in content, "oot_reloaded.o2r archive loaded"):
        passed += 1

    print(f"\n[7.x] Phase 7 summary: {passed}/{total} passed")
    return passed, total
