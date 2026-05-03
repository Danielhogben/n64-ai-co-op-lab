import json
import subprocess
from pathlib import Path
from helpers import assert_true
from engine_connector import EngineConnector

def run():
    print("\n" + "="*60)
    print("PHASE 3: ENGINE API & DM CONNECTIVITY")
    print("="*60 + "\n")

    ec = EngineConnector()
    passed = 0; total = 0

    print("[3.1] Engine process & log access:")
    total += 1
    if assert_true(ec.is_engine_running(), "Engine process detected"):
        passed += 1

    total += 1
    tail = ec.tail_log(200)
    if assert_true(len(tail) > 0, "Recent engine log output available"):
        passed += 1

    print("\n[3.2] Sail bridge activation:")
    total += 1
    if assert_true("SailBridge" in tail and "Connected to Sail server" in tail,
                   "SailBridge handshake logged"):
        passed += 1

    print("\n[3.3] DM campaign startup:")
    total += 1
    if assert_true("Dungeon Master Campaign STARTED" in tail,
                   "DM campaign started message logged"):
        passed += 1

    total += 1
    if assert_true("Nexus says:" in tail or "Nexus:" in tail,
                   "Nexus AI companion speaking"):
        passed += 1

    print("\n[3.4] Skill module load verification:")
    total += 1
    if assert_true("Loaded 16 skill modules" in tail,
                   "All 16 skill modules loaded"):
        passed += 1

    skills = [
        "ai_companion", "base_building", "combat_system", "dungeon_master",
        "economy_system", "factory_production", "inventory_management",
        "pentest_system", "player_progression", "pokemon_system",
        "quest_system", "reputation_system", "rom_integrator",
        "ship_management", "testing_system", "zone_navigation"
    ]
    for skill in skills:
        total += 1
        if assert_true(f"Loaded skill: {skill}" in tail, f"  skill {skill}"):
            passed += 1

    print("\n[3.5] State persistence:")
    total += 1
    state = ec.get_state()
    if assert_true(state is not None, "current_state.json readable"):
        passed += 1
        total += 1
        if assert_true("tick" in state, "State contains tick counter"):
            passed += 1
        total += 1
        if assert_true("dm_active" in state and state["dm_active"],
                       "DM active flag true"):
            passed += 1
        total += 1
        gs = state.get("game_state", {})
        player = gs.get("player", {})
        if assert_true("health" in player, "Player health tracked in state"):
            passed += 1

    print(f"\n[3.x] Phase 3 summary: {passed}/{total} passed")
    return passed, total
