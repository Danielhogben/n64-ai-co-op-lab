#!/usr/bin/env python3
"""Master test runner — no dynamic imports, explicit module loading."""

import sys, time, json, subprocess, argparse
from pathlib import Path

BASE = Path.home() / "HylianModding" / "AI_DM"
sys.path.insert(0, str(BASE))

# Import test modules and monitor
from test_suite.engine_connector import EngineConnector
from test_suite.test_services           import run as test_services_run, ServiceMonitor
from test_suite.test_mod_integrity      import run as test_mod_integrity_run
from test_suite.test_engine_api         import run as test_engine_api_run
from test_suite.test_gameplay_features  import run as test_gameplay_features_run
from test_suite.test_engine_commands    import run as test_engine_commands_run
from test_suite.test_sail_bridge        import run as test_sail_bridge_run
from test_suite.test_game_log           import run as test_game_log_run
from test_suite.test_mod_manifest_match import run as test_mod_manifest_match_run
from test_suite.test_performance        import run as test_performance_run
from test_suite.test_security           import run as test_security_run
from test_suite.test_regression         import run as test_regression_run
from test_suite.test_asset_pipeline     import run as test_asset_pipeline_run

PHASES = [
    ("Services & Connectivity", test_services_run),
    ("Mod Integrity",            test_mod_integrity_run),
    ("Engine API",               test_engine_api_run),
    ("Gameplay Features",        test_gameplay_features_run),
    ("Engine Commands",          test_engine_commands_run),
    ("Sail Bridge",              test_sail_bridge_run),
    ("Game Log",                 test_game_log_run),
    ("Manifest Consistency",     test_mod_manifest_match_run),
    ("Performance",              test_performance_run),
    ("Security",                 test_security_run),
    ("Regression",               test_regression_run),
    ("Asset Pipeline",           test_asset_pipeline_run),
]

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
    return (name, mod.run)

def main():
    parser = argparse.ArgumentParser(description="Project Nexus Mod Test Suite")
    parser.add_argument("--phase", type=int, help="Run single phase only")
    parser.add_argument("--list", action="store_true", help="List available phases")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--monitor", action="store_true", help="Start background service monitor")
    parser.add_argument("--monitor-interval", type=int, default=5, help="Monitor interval seconds (default 5)")
    parser.add_argument("--monitor-log", type=str, default=str(Path.home()/"HylianModding/AI_DM/monitor.log"),
                        help="Monitor log path")
    args = parser.parse_args()

    if args.list:
        print("Available test phases:")
        for i in range(1, 13):
            name, _ = load_phase(i)
            print(f"  {i:2}. {name}")
        return 0

    monitor = None
    if args.monitor:
        monitor = ServiceMonitor(interval=args.monitor_interval, log_path=args.monitor_log)
        monitor.start()
        time.sleep(1)  # Let first check complete

    try:
        if args.phase:
            phases_to_run = [load_phase(args.phase)]
        else:
            phases_to_run = [load_phase(i) for i in range(1, 13)]

        if not args.quiet:
            print("="*60)
            print("PROJECT NEXUS — AI FULL UNIVERSE MOD TEST SUITE")
            print("="*60)
            print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Wait for engine ready (max 15s)
        ec = EngineConnector()
        if not args.quiet:
            print("[*] Waiting for engine ready signal...")
        ready = ec.wait_for_ready(15)
        if not args.quiet:
            print(f"  {'✓ Ready' if ready else '⚠ Not confirmed — proceeding'}\n")

        total_passed = 0; total_cases = 0; results = []

        for phase_name, runner in phases_to_run:
            if not args.quiet:
                print(f"\n{'='*60}")
                print(f"PHASE: {phase_name.upper()}")
                print('='*60)
            try:
                passed, total = runner()
                total_passed += passed; total_cases += total
                results.append((phase_name, passed, total))
            except Exception as e:
                if not args.quiet:
                    print(f"  ✗ Phase '{phase_name}' CRASHED: {e}")
                    import traceback; traceback.print_exc()
                results.append((phase_name, 0, 0))

        # Final summary
        if not args.quiet:
            print("\n" + "="*60)
            print("FINAL RESULTS")
            print("="*60)
        for phase_name, passed, total in results:
            pct = (passed / total * 100) if total > 0 else 0
            if args.json:
                print(json.dumps({"phase": phase_name, "passed": passed, "total": total, "percent": round(pct,1)}))
            else:
                bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                print(f"  {phase_name:.<30} {passed}/{total} [{bar}] {pct:.0f}%")
        grand_total = sum(t for _, _, t in results)
        grand_passed = sum(p for _, p, _ in results)
        pct = (grand_passed / grand_total * 100) if grand_total > 0 else 0
        if not args.quiet:
            print(f"\n  GRAND TOTAL: {grand_passed}/{grand_total} — {pct:.0f}%")
            if   pct >= 90: print("  STATUS: ✓ EXCELLENT — production-ready");      rc = 0
            elif pct >= 70: print("  STATUS: ✓ GOOD — minor issues");               rc = 0
            elif pct >= 50: print("  STATUS: ⚠ FAIR — needs attention");            rc = 1
            else:            print("  STATUS: ✗ CRITICAL — blocking issues");        rc = 2
            print()
        else:
            rc = 0 if pct >= 70 else 1
        return rc
    finally:
        if monitor:
            monitor.stop()

if __name__ == "__main__":
    sys.exit(main())
