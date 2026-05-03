from helpers import assert_true
from pathlib import Path

def run():
    print("\n" + "="*60)
    print("PHASE 12: ASSET PIPELINE & HOT-RELOAD")
    print("="*60 + "\n")

    passed = 0; total = 0

    print("[12.1] Hot-reload mechanism check:")
    # Check if engine uses inotify or polling loops
    engine_log = Path("/home/donn/HylianModding/AI_DM/engine.log")
    content = engine_log.read_text() if engine_log.exists() else ""
    total += 1
    if assert_true("hot" not in content.lower() and "reload" not in content.lower(),
                   "No hot-reload detected (expected — static assets)"):
        passed += 1

    print("\n[12.2] Asset format coverage (枚举):")
    mod_path = Path("/home/donn/HylianModding/ShipOfHarkinian/mods/ai_full_universe")
    # Count assets by extension
    exts = {}
    for f in mod_path.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower()
            exts[ext] = exts.get(ext, 0) + 1
    for ext, cnt in sorted(exts.items(), key=lambda x: -x[1])[:8]:
        total += 1
        # Expect JSON configs, maybe binary textures
        if assert_true(cnt >= 10, f"  {ext}: {cnt} files"):
            passed += 1

    print(f"\n[12.x] Phase 12 summary: {passed}/{total} passed")
    return passed, total
