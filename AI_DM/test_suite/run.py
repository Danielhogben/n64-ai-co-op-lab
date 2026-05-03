#!/usr/bin/env python3
"""Master test runner — no dynamic imports, explicit module loading."""

import sys, time, json, subprocess
from pathlib import Path

BASE = Path.home() / "HylianModding" / "AI_DM"
sys.path.insert(0, str(BASE))

# Import directly
from test_suite.engine_connector import EngineConnector
from test_suite.test_services           import run as test_services_run
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

def main():
    print("="*60)
    print("PROJECT NEXUS — AI FULL UNIVERSE MOD TEST SUITE")
    print("="*60)
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")

    # Wait for engine ready signal (max 15s)
    ec = EngineConnector()
    print("[*] Waiting for engine ready signal...")
    ready = ec.wait_for_ready(15)
    print(f"  {'✓ Ready' if ready else '⚠ Not confirmed — proceeding'}\\n")

    total_passed = 0
    total_cases = 0
    results = []

    for phase_name, runner in PHASES:
        print(f"\n{'='*60}")
        print(f"PHASE: {phase_name.upper()}")
        print('='*60)
        try:
            passed, total = runner()
            total_passed += passed
            total_cases += total
            results.append((phase_name, passed, total))
        except Exception as e:
            print(f"  ✗ Phase '{phase_name}' CRASHED: {e}")
            import traceback; traceback.print_exc()
            results.append((phase_name, 0, 0))

    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for phase_name, passed, total in results:
        pct = (passed / total * 100) if total > 0 else 0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"  {phase_name:.<30} {passed}/{total} [{bar}] {pct:.0f}%")
    grand_total = sum(t for _, _, t in results)
    grand_passed = sum(p for _, p, _ in results)
    pct = (grand_passed / grand_total * 100) if grand_total > 0 else 0
    print(f"\\n  GRAND TOTAL: {grand_passed}/{grand_total} — {pct:.0f}%")
    print()

    if   pct >= 90: print("  STATUS: ✓ EXCELLENT — production-ready");      rc = 0
    elif pct >= 70: print("  STATUS: ✓ GOOD — minor issues");               rc = 0
    elif pct >= 50: print("  STATUS: ⚠ FAIR — needs attention");            rc = 1
    else:            print("  STATUS: ✗ CRITICAL — blocking issues");        rc = 2

    return rc

if __name__ == "__main__":
    sys.exit(main())
