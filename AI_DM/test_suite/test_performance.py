import subprocess
from helpers import assert_true

def run():
    print("\n" + "="*60)
    print("PHASE 9: PERFORMANCE & STABILITY")
    print("="*60 + "\n")

    passed = 0; total = 0
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    # Filter header and blank lines
    lines = [l for l in result.stdout.split('\n') if l and 'RSS' not in l and 'COMMAND' not in l]

    print("[9.1] Engine memory:")
    eng = [l for l in lines if 'python' in l.lower() and 'engine/main.py' in l]
    if eng and len(eng[0].split()) >= 6:
        rss = float(eng[0].split()[5]) / 1024
        total += 1
        if assert_true(rss < 2000, f"Engine memory < 2000 MB  →  {rss:.0f} MB"):
            passed += 1

    print("\n[9.2] Engine CPU baseline:")
    if eng:
        cpu = float(eng[0].split()[2])
        total += 1
        if assert_true(cpu < 80, f"Engine CPU < 80%  →  {cpu:.1f}%"):
            passed += 1

    print("\n[9.3] Sail memory:")
    sail = [l for l in lines if 'deno' in l.lower() and 'sail_server' in l]
    if sail and len(sail[0].split()) >= 6:
        rss = float(sail[0].split()[5]) / 1024
        total += 1
        if assert_true(rss < 500, f"Sail memory < 500 MB  →  {rss:.0f} MB"):
            passed += 1

    print("\n[9.4] Game client memory:")
    soh = [l for l in lines if 'soh' in l.lower() and 'appimage' in l.lower()]
    if soh and len(soh[0].split()) >= 6:
        rss = float(soh[0].split()[5]) / 1024
        total += 1
        if assert_true(rss < 4000, f"SoH memory < 4000 MB  →  {rss:.0f} MB"):
            passed += 1

    print(f"\n[9.x] Phase 9 summary: {passed}/{total} passed")
    return passed, total
