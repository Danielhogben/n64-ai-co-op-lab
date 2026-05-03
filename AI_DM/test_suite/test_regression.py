import json
from pathlib import Path
from helpers import assert_true

def run():
    print("\n" + "="*60)
    print("PHASE 11: REGRESSION & STATE PERSISTENCE")
    print("="*60 + "\n")

    state_path = Path("/home/donn/HylianModding/AI_DM/current_state.json")
    passed = 0; total = 0

    print("[11.1] State file persistence:")
    total += 1
    if assert_true(state_path.exists(), "State file exists"):
        passed += 1

    try:
        with open(state_path) as f:
            state = json.load(f)
    except:
        print("  ✗ State file unreadable")
        return 0, 0

    print("\n[11.2] Core state keys:")
    for key in ["tick", "game_state", "dm_active", "timestamp"]:
        total += 1
        if assert_true(key in state, f"  {key}"):
            passed += 1

    gs = state.get("game_state", {})
    print("\n[11.3] Game state structure:")
    for key in ["player", "world", "enemies", "active_events"]:
        total += 1
        if assert_true(key in gs, f"  game_state.{key}"):
            passed += 1

    player = gs.get("player", {})
    print("\n[11.4] Player tracking:")
    for key in ["health", "score", "x", "y", "weapon"]:
        total += 1
        if assert_true(key in player, f"  player.{key}"):
            passed += 1

    total += 1
    if assert_true(isinstance(player.get("health"), (int, float)), "Health is numeric"):
        passed += 1

    print(f"\n[11.x] Phase 11 summary: {passed}/{total} passed")
    return passed, total
