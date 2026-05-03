import json
from pathlib import Path
from helpers import assert_true

def run():
    print("\n" + "="*60)
    print("PHASE 8: MANIFEST VS FILESYSTEM CONSISTENCY")
    print("="*60 + "\n")

    mod_path = Path("/home/donn/HylianModding/ShipOfHarkinian/mods/ai_full_universe")
    manifest = mod_path / "manifest.json"
    passed = 0; total = 0

    try:
        with open(manifest) as f:
            mdata = json.load(f)
        stats = mdata.get("stats", {})
    except:
        print("  ✗ Cannot read manifest")
        return 0, 0

    expected_roms    = stats.get("total_roms", 0)
    expected_galaxies = stats.get("total_galaxies", 0)
    expected_zones   = stats.get("total_zones", 0)
    expected_pokemon = stats.get("pokemon_companions", 0)

    print(f"  ROMs expected      : {expected_roms}")
    print(f"  Galaxies expected  : {expected_galaxies}")
    print(f"  Zones expected     : {expected_zones}")
    print(f"  Pokemon expected   : {expected_pokemon}")

    # Check galaxy JSON files exist (8 files, not subdirectories)
    galaxies_dir = mod_path / "galaxies"
    if galaxies_dir.exists():
        galaxy_files = list(galaxies_dir.glob("*.json"))
        # Count non-manifest JSON files
        galaxy_count = len([f for f in galaxy_files if f.name != "manifest.json"])
        total += 1
        if assert_true(galaxy_count >= expected_galaxies,
                       f"galaxy JSON files >= {expected_galaxies} (found {galaxy_count})"):
            passed += 1

    print("\n[8.2] Zone definitions (zones.json manifest):")
    zones_file = mod_path / "zones.json"
    total += 1
    if assert_true(zones_file.exists(), "zones.json present"):
        passed += 1
        try:
            with open(zones_file) as f:
                zdata = json.load(f)
            zone_list = zdata.get('zones', zdata.get('zone_list', zdata.get('zones_list', [])))
            total += 1
            if assert_true(len(zone_list) >= expected_zones,
                           f"zones in zones.json >= {expected_zones} (found {len(zone_list)})"):
                passed += 1
        except Exception as e:
            print(f"  ⚠ zones.json parse: {e}")

    print("\n[8.3] Enemy definitions:")
    enemies_dir = mod_path / "enemies"
    if enemies_dir.exists():
        enemy_files = list(enemies_dir.rglob("*.json"))
        total += 1
        if assert_true(len(enemy_files) >= 100, f"Enemy files >= 100 (found {len(enemy_files)})"):
            passed += 1

    print("\n[8.4] Item definitions:")
    items_dir = mod_path / "items"
    if items_dir.exists():
        item_files = list(items_dir.rglob("*.json"))
        total += 1
        if assert_true(len(item_files) >= 200, f"Item files >= 200 (found {len(item_files)})"):
            passed += 1

    print("\n[8.5] Quest definitions:")
    quests_dir = mod_path / "quests"
    if quests_dir.exists():
        quest_files = list(quests_dir.rglob("*.json"))
        total += 1
        if assert_true(len(quest_files) >= 5, f"Quest files >= 5 (found {len(quest_files)})"):
            passed += 1

    print(f"\n[8.x] Phase 8 summary: {passed}/{total} passed")
    return passed, total
