import sys, os
# Add the project directory to path
sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))

from engine.registry import reg
from engine.skills.rom_integrator import ROMIntegrator

# Setup registry config (as main.py does)
reg.config = {
    "mod_path": os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe"),
    "rom_database": os.path.expanduser("~/HylianModding/AI_DM/rom_database.json"),
}

# Load ROM database into registry
import json
with open(reg.config["rom_database"]) as f:
    reg.rom_database = json.load(f)

# Load existing zones (if any)
zones_path = os.path.join(reg.config["mod_path"], "zones.json")
if os.path.exists(zones_path):
    with open(zones_path) as f:
        reg.zones = json.load(f)

print("🚀 Starting ROM Integration...")
integrator = ROMIntegrator()
report = integrator.full_integration(dry_run=False)

print("\n✅ Integration Report:")
print(json.dumps(report, indent=2))
print("\nFiles generated in:", reg.config["mod_path"])
