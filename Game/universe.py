"""Load and manage the AI Full Universe data."""
import json, os, random

GAME_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(path):
    full = os.path.expanduser(path)
    if os.path.exists(full):
        with open(full) as f:
            return json.load(f)
    return {}

class Universe:
    def __init__(self):
        self.rom_db = load_json("~/HylianModding/AI_DM/rom_database.json")
        self.galaxies = []
        self.zones = []
        self.companions = []
        self.ai_companion = {}
        self.load_universe()

    def load_universe(self):
        gal_dir = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe/galaxies")
        if os.path.exists(gal_dir):
            manifest = load_json(os.path.join(gal_dir, "manifest.json"))
            for i in range(manifest.get("total_galaxies", 0)):
                g = load_json(os.path.join(gal_dir, f"galaxy_{i}.json"))
                if g:
                    self.galaxies.append(g)

        zones_path = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe/zones.json")
        self.zones = load_json(zones_path) or []

        comp_dir = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe/pokemon_companions")
        if os.path.exists(comp_dir):
            for f in sorted(os.listdir(comp_dir)):
                if f.startswith("companion_") and f.endswith(".json"):
                    c = load_json(os.path.join(comp_dir, f))
                    if c:
                        self.companions.append(c)

        ai_path = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe/ai_companion/ai_companion.json")
        self.ai_companion = load_json(ai_path) or {"name": "Nexus", "personality": "wise"}

    def get_roms(self):
        return self.rom_db.get("roms", [])

    def get_random_enemy(self, danger="medium"):
        templates = [
            {"name": "Shadow Drone", "hp": 30, "dmg": 5, "speed": 3, "color": (80, 0, 120)},
            {"name": "Skulltula Swarm", "hp": 50, "dmg": 8, "speed": 2, "color": (150, 100, 0)},
            {"name": "Dark Link Elite", "hp": 80, "dmg": 12, "speed": 4, "color": (20, 20, 40)},
            {"name": "Space Octorok", "hp": 25, "dmg": 4, "speed": 3, "color": (200, 50, 50)},
            {"name": "AI Sentinel", "hp": 100, "dmg": 15, "speed": 2, "color": (0, 200, 200)},
        ]
        if danger == "extreme":
            templates = [{**t, "hp": t["hp"]*2, "dmg": t["dmg"]*2} for t in templates]
        elif danger == "high":
            templates = [{**t, "hp": int(t["hp"]*1.5), "dmg": int(t["dmg"]*1.5)} for t in templates]
        e = random.choice(templates).copy()
        e["id"] = f"enemy_{random.randint(1000,9999)}"
        return e
