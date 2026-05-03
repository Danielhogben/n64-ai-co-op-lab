#!/usr/bin/env python3
"""Full test runner for Project Nexus mod validation.

Usage:
  python3 run_tests.py              # run all phases
  python3 run_tests.py --phase 1    # run specific phase only
  python3 run_tests.py --list       # list phases
  python3 run_tests.py --json       # machine-readable output
"""

import sys, time, argparse, subprocess
from pathlib import Path

def load_phase(phase_id):
    mapping = {
        1: ("Services & Connectivity", "test_services"),
        2: ("Mod Integrity", "test_mod_integrity"),
        3: ("Engine API", "test_engine_api"),
        4: ("Gameplay Features", "test_gameplay_features"),
        5: ("Engine Commands", "test_engine_commands"),
        6: ("Sail Bridge", "test_sail_bridge"),
        7: ("Game Log", "test_game_log"),
        8: ("Manifest Consistency", "test_mod_manifest_match"),
        9: ("Performance", "test_performance"),
        10: ("Security", "test_security"),
        11: ("Regression", "test_regression"),
        12: ("Asset Pipeline", "test_asset_pipeline"),
    }
    if phase_id not in mapping:
        return None
    name, mod_name = mapping[phase_id]
    mod = __import__(f"test_suite.{mod_name}", fromlist=[mod_name])
    return (name, mod)

def main():
    parser = argparse.ArgumentParser(description="Project Nexus Mod Test Suite")
    parser.add_argument("--phase", type=int, help="Run single phase only")
    parser.add_argument("--list", action="store_true", help="List available phases")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    args = parser.parse_args()

    if args.list:
        print("Available test phases:")
        for i in range(1, 13):
            name, _ = load_phase(i)
            print(f"  {i:2}. {name}")
        return 0

    phases_to_run = []
    if args.phase:
        phase = load_phase(args.phase)
        if not phase:
            print(f"ERROR: Invalid phase ID {args.phase}")
            return 1
        phases_to_run = [phase]
    else:
        phases_to_run = [load_phase(i) for i in range(1, 13)]

    if not args.quiet:
        print("="*60)
        print("PROJECT NEXUS — AI FULL UNIVERSE MOD TEST SUITE")
        print("="*60)
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")

    # Wait for engine to be ready before starting
    if not args.quiet:
        print("[*] Waiting for engine readiness...")
    for _ in range(20):
        try:
            result = subprocess.run(
                ["tail", "-20", "/home/donn/HylianModding/AI_DM/engine.log"],
                capture_output=True, text=True
            )
            if "ENGINE READY" in result.stdout or "Engine ready" in result.stdout:
                if not args.quiet:
                    print("  ✓ Engine ready detected\\n")
                break
        except:
            pass
        time.sleep(0.5)
    else:
        if not args.quiet:
            print("  ⚠ Engine ready not confirmed within timeout (proceeding anyway)\\n")

    total_passed = 0
    total_cases = 0
    results = []

    for phase_name, module in phases_to_run:
        if not args.quiet:
            print(f"\\n{'='*60}")
            print(f"PHASE: {phase_name.upper()}")
            print('='*60)
        try:
            passed, total = module.run()
            total_passed += passed
            total_cases += total
            results.append((phase_name, passed, total))
        except Exception as e:
            if not args.quiet:
                print(f"  ✗ Phase '{phase_name}' CRASHED: {e}")
                import traceback; traceback.print_exc()
            results.append((phase_name, 0, 0))

    # Summary
    if not args.quiet:
        print("\\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
    for phase_name, passed, total in results:
        pct = (passed / total * 100) if total > 0 else 0
        if args.json:
            print(json.dumps({
                "phase": phase_name,
                "passed": passed,
                "total": total,
                "percent": round(pct, 1)
            }))
        else:
            bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
            print(f"  {phase_name:.<30} {passed}/{total} [{bar}] {pct:.0f}%")

    grand_total = sum(t for _, _, t in results)
    grand_passed = sum(p for _, p, _ in results)
    pct = (grand_passed / grand_total * 100) if grand_total > 0 else 0

    if not args.quiet:
        print()
        print(f"  GRAND TOTAL: {grand_passed}/{grand_total} — {pct:.0f}%")
        if pct >= 90:
            print("\\n  STATUS: ✓ EXCELLENT — Mod is production-ready")
        elif pct >= 70:
            print("\\n  STATUS: ✓ GOOD — Minor issues may exist")
        elif pct >= 50:
            print("\\n  STATUS: ⚠ FAIR — Some work needed")
        else:
            print("\\n  STATUS: ✗ CRITICAL — Blocking issues detected")
        print()

    return 0 if pct >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())
