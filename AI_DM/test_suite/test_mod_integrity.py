import json
from pathlib import Path
from helpers import assert_true
from engine_connector import EngineConnector

def run():
    print("\n" + "="*60)
    print("PHASE 2: MOD INTEGRITY & CONTENT VALIDATION")
    print("="*60 + "\n")

    mod_path = Path("/home/donn/HylianModding/ShipOfHarkinian/mods/ai_full_universe")
    ec = EngineConnector()
    passed = 0; total = 0

    print("[2.1] Mod directory structure:")
    total += 1
    if assert_true(mod_path.exists(), "ai_full_universe directory exists"):
        passed += 1

    manifest = mod_path / "manifest.json"
    total += 1
    if assert_true(manifest.exists(), "manifest.json present"):
        passed += 1
        try:
            with open(manifest) as f:
                data = json.load(f)

            # Core identity
            total += 1
            if assert_true(data.get("id") == "ai_full_universe", "manifest id correct"):
                passed += 1

            # Stats validation
            stats = data.get("stats", {})
            checks = [
                (stats.get("total_roms",0) >= 300, f"ROMs >= 300 (found {stats.get('total_roms')})"),
                (stats.get("total_galaxies",0) == 8, f"Galaxies = 8 (found {stats.get('total_galaxies')})"),
                (stats.get("total_zones",0) >= 50,  f"Zones >= 50 (found {stats.get('total_zones')})"),
                (stats.get("pokemon_companions",0) >= 5, f"Pokemon companions >= 5 (found {stats.get('pokemon_companions')})"),
            ]
            for cond, msg in checks:
                total += 1
                if assert_true(cond, msg):
                    passed += 1
        except Exception as e:
            print(f"  ✗ manifest error: {e}")
            total += 4

    total += 1
    if assert_true((mod_path / "universe_config.json").exists(), "universe_config.json present"):
        passed += 1

    print("\n[2.2] Required subdirectories:")
    required_dirs = ["enemies", "items", "quests", "galaxies", "ships", "factories", "ai_companion", "base_building"]
    for d in required_dirs:
        total += 1
        if assert_true((mod_path / d).exists() and (mod_path / d).is_dir(), f"  {d}/"):
            passed += 1

    # Zones stored in flat zones.json, not a directory
    total += 1
    if assert_true((mod_path / "zones.json").exists(), "zones.json present (flat zone list)"):
        passed += 1

    # Galaxy directory is present; verify it holds JSON definitions
    total += 1
    galaxies_dir = mod_path / "galaxies"
    gfiles = list(galaxies_dir.glob("*.json")) if galaxies_dir.exists() else []
    gcount = len([f for f in gfiles if f.name != "manifest.json"])
    if assert_true(gcount >= 8, f"galaxies/ contains >=8 JSON defs (found {gcount})"):
        passed += 1

    print("\n[2.3] Generated content (per-category subdirectories):")
    for cat in ['enemies', 'items', 'quests']:
        gen_path = mod_path / cat / 'generated'
        total += 1
        if gen_path.exists() and any(gen_path.iterdir()):
            count = len(list(gen_path.iterdir()))
            if assert_true(True, f"  {cat}/generated/ populated ({count} files)"):
                passed += 1
        else:
            if assert_true(False, f"  {cat}/generated/ MISSING or empty"):
                passed += 1

    print("\n[2.4] Mod size sanity:")
    all_files = list(mod_path.rglob("*"))
    total_files = len([f for f in all_files if f.is_file()])
    total += 1
    if assert_true(total_files > 1000, f"Total file count > 1000 (found {total_files})"):
        passed += 1

    print(f"\n[2.x] Phase 2 summary: {passed}/{total} passed")
    return passed, total
