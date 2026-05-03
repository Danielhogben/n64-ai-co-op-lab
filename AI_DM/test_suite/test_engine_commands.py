from helpers import assert_true
from engine_connector import EngineConnector

def run():
    print("\n" + "="*60)
    print("PHASE 5: ENGINE COMMAND & DM INTERFACE")
    print("="*60 + "\n")

    ec = EngineConnector()
    passed = 0; total = 0
    tail = ec.tail_log(500)

    print("[5.1] Engine availability:")
    total += 1
    if assert_true(ec.is_engine_running(), "Engine process alive"):
        passed += 1

    print("\n[5.2] Skill module inventory (16 expected):")
    total += 1
    if assert_true("Loaded 16 skill modules" in tail, "16 skill modules loaded"):
        passed += 1

    skills = [
        "testing_system", "zone_navigation", "ai_companion",
        "base_building", "combat_system", "dungeon_master",
        "economy_system", "factory_production", "inventory_management",
        "pentest_system", "player_progression", "pokemon_system",
        "quest_system", "reputation_system", "rom_integrator", "ship_management"
    ]
    for skill in skills:
        total += 1
        if assert_true(f"Loaded skill: {skill}" in tail, f"  {skill}"):
            passed += 1

    print("\n[5.3] DM initialization:")
    total += 1
    if assert_true("Dungeon Master Campaign STARTED" in tail, "DM campaign started"):
        passed += 1
    total += 1
    if assert_true("Nexus says:" in tail or "Nexus:" in tail, "Nexus speaking"):
        passed += 1

    print("\n[5.4] Integration startup flow:")
    total += 1
    if assert_true("Integrator Init" in tail, "rom_integrator initialized"):
        passed += 1
    total += 1
    if assert_true("SailBridge" in tail and "Connected" in tail, "Sail bridge connected"):
        passed += 1

    print(f"\n[5.x] Phase 5 summary: {passed}/{total} passed")
    return passed, total
