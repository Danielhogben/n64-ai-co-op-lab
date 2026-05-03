import json
from pathlib import Path
from helpers import assert_true

def run():
    print("\n" + "="*60)
    print("PHASE 4: GAMEPLAY FEATURE VALIDATION")
    print("="*60 + "\n")

    mod_path = Path("/home/donn/HylianModding/ShipOfHarkinian/mods/ai_full_universe")
    manifest = mod_path / "manifest.json"
    config = mod_path / "universe_config.json"
    passed = 0; total = 0

    try:
        with open(manifest) as f:
            mdata = json.load(f)
        features = mdata.get("features", {})
        stats = mdata.get("stats", {})
    except:
        print("  ✗ Could not read manifest")
        return 0, 0

    print("[4.1] Core feature flags (12 checks):")
    feature_checks = [
        ("open_universe", "Open universe travel"),
        ("seamless_travel", "Seamless transitions"),
        ("pokemon_companions", "Pokemon companions"),
        ("ai_companion", "AI companion Nexus"),
        ("zeroclaw_integration", "ZeroClaw integration"),
        ("space_combat", "Space combat"),
        ("base_building", "Base building"),
        ("resource_mining", "Resource mining"),
        ("alien_encounters", "Alien encounters"),
        ("boss_battles", "Boss battles"),
        ("dynamic_weather", "Dynamic weather"),
        ("day_night_cycle", "Day/night cycle"),
    ]
    for key, label in feature_checks:
        total += 1
        if assert_true(features.get(key, False), f"  {label}"):
            passed += 1

    print("\n[4.2] Universe scale validation:")
    total += 1
    if assert_true(stats.get("total_roms", 0) >= 300,
                   f"ROMs integrated: {stats.get('total_roms')}"):
        passed += 1
    total += 1
    if assert_true(stats.get("total_galaxies", 0) == 8,
                   f"Galaxies: {stats.get('total_galaxies')}"):
        passed += 1
    total += 1
    if assert_true(stats.get("total_zones", 0) >= 50,
                   f"Zones: {stats.get('total_zones')}"):
        passed += 1
    total += 1
    if assert_true(stats.get("pokemon_companions", 0) >= 5,
                   f"Pokemon companions: {stats.get('pokemon_companions')}"):
        passed += 1

    print("\n[4.3] Universe config gameplay:")
    try:
        with open(config) as f:
            ucfg = json.load(f)
        gameplay = ucfg.get("gameplay", {})
        for key in ["player_role", "main_quest", "side_quests", "win_condition"]:
            total += 1
            if assert_true(gameplay.get(key), f"  gameplay.{key} defined"):
                passed += 1
    except:
        total += 4

    print(f"\n[4.x] Phase 4 summary: {passed}/{total} passed")
    return passed, total
