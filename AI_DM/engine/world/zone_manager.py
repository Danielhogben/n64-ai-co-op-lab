"""Galaxy map: manages 12 galaxies, warp lanes, faction control."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from registry import reg

GALAXY_CONFIG = {
    "milky_way": {"zones": ["zone_0","zone_1","zone_2","zone_3"], "factions": ["player","zora","goron"]},
    "andromeda": {"zones": ["zone_4","zone_5","zone_6"], "factions": ["krogan","salarian","asari"]},
    "phoenix": {"zones": ["zone_7","zone_8"], "factions": ["player","ai"]},
    "whirlpool": {"zones": ["zone_9","zone_10","zone_11"], "factions": ["pirate","federal"]},
    "serpentis": {"zones": ["zone_12","zone_13"], "factions": ["player","trade"]},
    "cygnus": {"zones": ["zone_14","zone_15","zone_16"], "factions": ["borg","federation"]},
    "fornax": {"zones": ["zone_17","zone_18"], "factions": ["player","romulan"]},
    "pegasus": {"zones": ["zone_19"], "factions": ["player","ancient"]},
}

class GalaxyMap:
    """Maintains galaxy/zone graph and warp connections."""
    
    def __init__(self):
        self.galaxies = GALAXY_CONFIG.copy()
        self._load_existing_zones()
    
    def _load_existing_zones(self):
        # Zones already exist in reg.zones
        pass
    
    def list_galaxies(self) -> List[Dict[str, Any]]:
        return [{"name": g, "zones": len(c["zones"]), "factions": c["factions"]} for g,c in self.galaxies.items()]
    
    def get_galaxy_zones(self, galaxy: str) -> List[str]:
        return self.galaxies.get(galaxy, {}).get("zones", [])
    
    def can_warp(self, from_zone: str, to_zone: str) -> bool:
        """Check if warp drive can reach."""
        # For now: all zones reachable (linear warp ranks later)
        return True
    
    def get_zone_galaxy(self, zone_id: str) -> str:
        for g, cfg in self.galaxies.items():
            if zone_id in cfg["zones"]:
                return g
        return "unknown"

class ZoneManager:
    """Handles zone loading/unloading, enemy spawns, difficulty scaling."""
    
    def __init__(self):
        self.zm = None
        self.active_zone = None
        self.entities = []  # list of {type, id, x, y, z}
    
    def load_zone(self, zone_id: str) -> Dict[str, Any]:
        """Load a zone from reg.zones."""
        for z in reg.zones:
            if z["id"] == zone_id:
                self.active_zone = z
                reg.player_state["current_zone"] = zone_id
                reg.emit("zone.enter", zone_id=zone_id)
                return z
        raise KeyError(f"Zone {zone_id} not found")
    
    def get_active(self) -> Dict[str, Any]:
        if not self.active_zone:
            raise RuntimeError("No active zone — must warp first")
        return self.active_zone
    
    def spawn_enemy(self, enemy_type: str, count: int = 1) -> List[Dict]:
        """Spawn enemies into current zone."""
        spawned = []
        for i in range(count):
            eid = f"enemy_{enemy_type}_{len(self.entities) + i}"
            enemy = {
                "id": eid,
                "type": enemy_type,
                "hp": 50,
                "max_hp": 50,
                "damage": 8,
                "zone": self.active_zone["id"],
                "position": {"x": 0, "y": 0, "z": 0},
            }
            self.entities.append(enemy)
            spawned.append(enemy)
        reg.emit("enemy.spawned", zone_id=self.active_zone["id"], count=count)
        return spawned
    
    def clear_zone(self):
        """Remove all entities from current zone."""
        self.entities = []
        reg.emit("zone.cleared", zone_id=self.active_zone["id"])

class Skill:
    def __init__(self):
        self.galaxy = GalaxyMap()
        self.zm = ZoneManager()
        self.commands = {
            "galaxies": self.cmd_galaxies,
            "galaxy_zones": self.cmd_galaxy_zones,
            "load": self.cmd_load,
            "active": self.cmd_active,
            "spawn": self.cmd_spawn,
            "clear": self.cmd_clear,
        }
    
    def cmd_galaxies(self, *args):
        """world galaxies — list all galaxies."""
        lines = ["Galaxy           Zones   Factions"]
        for g in self.galaxy.list_galaxies():
            lines.append(f"{g['name']:15} {len(g['zones']):7} {', '.join(g['factions'])}")
        return "\n".join(lines)
    
    def cmd_galaxy_zones(self, galaxy: str, *args):
        """world galaxy_zones <galaxy_name> — list zones in a galaxy."""
        zones = self.galaxy.get_galaxy_zones(galaxy)
        return f"Zones in {galaxy}: {', '.join(zones)}"
    
    def cmd_load(self, zone_id: str, *args):
        """world load <zone_id> — load zone into memory."""
        try:
            z = self.zm.load_zone(zone_id)
            return f"Loaded zone {zone_id}: {z['name']} ({z.get('size')})"
        except KeyError as e:
            return str(e)
    
    def cmd_active(self, *args):
        """world active — show current active zone."""
        if not self.zm.active_zone:
            return "No zone loaded. Use 'world load <zone_id>'"
        z = self.zm.active_zone
        return f"Active: {z['name']} ({z['id']}) | Entities: {len(self.zm.entities)}"
    
    def cmd_spawn(self, enemy_type: str, count: str = "1", *args):
        """world spawn <enemy_type> [count] — spawn enemies in active zone."""
        if not self.zm.active_zone:
            return "Load a zone first: world load <zone_id>"
        cnt = int(count)
        spawned = self.zm.spawn_enemy(enemy_type, cnt)
        return f"Spawned {len(spawned)} {enemy_type} enemies in {self.zm.active_zone['id']}"
    
    def cmd_clear(self, *args):
        """world clear — remove all entities from active zone."""
        if not self.zm.active_zone:
            return "No zone loaded"
        self.zm.clear_zone()
        return f"Cleared all entities from {self.zm.active_zone['id']}"
