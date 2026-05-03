"""Base Building Skill — construct, upgrade, and manage base buildings."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import BASE_BUILT
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import BASE_BUILT

class BaseManager:
    """Manages 8 base building types across zones."""
    
    def __init__(self):
        self.bases_path = os.path.join(reg.config.get("mod_path", ""), "base_building")
        self.zones_path = os.path.join(reg.config.get("mod_path", ""), "zones.json")
        os.makedirs(self.bases_path, exist_ok=True)
        
    def list_bases(self) -> List[Dict[str, Any]]:
        bases = []
        for f in sorted(os.listdir(self.bases_path)):
            if f.startswith("base_") and f.endswith(".json"):
                with open(os.path.join(self.bases_path, f)) as fp:
                    data = json.load(fp)
                bases.append({
                    "id": data["id"],
                    "type": data.get("building_type", "unknown"),
                    "zone": data.get("zone_id", "?"),
                    "level": data.get("level", 1),
                    "health": data.get("health", 100),
                    "power_use": data.get("power_use", 0),
                })
        return bases
    
    def get_base(self, base_id: str) -> Dict[str, Any]:
        path = os.path.join(self.bases_path, f"{base_id}.json")
        with open(path) as f:
            return json.load(f)
    
    def save_base(self, base_id: str, data: Dict[str, Any]):
        path = os.path.join(self.bases_path, f"{base_id}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        reg.emit(BASE_BUILT, base_id=base_id, zone_id=data.get("zone_id"))
    
    def construct(self, zone_id: str, building_type: str, level: int = 1) -> str:
        """Build a new base in a zone."""
        # Check zone exists and has capacity
        if os.path.exists(self.zones_path):
            with open(self.zones_path) as f:
                zones = json.load(f)
            zone = next((z for z in zones if z["id"] == zone_id), None)
            if not zone:
                return f"Unknown zone: {zone_id}"
            current_buildings = zone.get("buildings", 0)
            max_buildings = zone.get("max_buildings", 5)
            if current_buildings >= max_buildings:
                return f"Zone {zone_id} at building capacity ({max_buildings})"
        else:
            return "zones.json not found"
        
        # Create base
        existing = os.listdir(self.bases_path)
        base_num = len([b for b in existing if b.startswith("base_") and b.endswith(".json")])
        base_id = f"base_{base_num}"
        
        base_data = {
            "id": base_id,
            "zone_id": zone_id,
            "building_type": building_type,
            "level": level,
            "health": 100 * level,
            "power_use": 50 * level,
            "storage": {"materials": 0, "credits": 0, "fuel": 0},
            "active_projects": [],
            "crew": level * 5,
            "defense_status": "online",
            "modules": [],
        }
        self.save_base(base_id, base_data)
        
        # Update zone building count
        if os.path.exists(self.zones_path):
            with open(self.zones_path) as f:
                zones = json.load(f)
            for z in zones:
                if z["id"] == zone_id:
                    z["buildings"] = z.get("buildings", 0) + 1
                    break
            with open(self.zones_path, 'w') as f:
                json.dump(zones, f, indent=2)
        
        return f"Constructed {building_type} ({base_id}) in zone {zone_id}"
    
    def upgrade(self, base_id: str, to_level: int) -> str:
        base = self.get_base(base_id)
        old = base["level"]
        base["level"] = to_level
        base["health"] = 100 * to_level
        base["power_use"] = 50 * to_level
        base["crew"] = to_level * 5
        self.save_base(base_id, base)
        return f"Upgraded {base_id} from L{old} → L{to_level}"
    
    def set_power(self, base_id: str, defense_pct: int, production_pct: int) -> str:
        base = self.get_base(base_id)
        total = defense_pct + production_pct
        if total != 100:
            return f"Power allocation must sum to 100% (got {defense_pct}/{production_pct})"
        base["power_allocation"] = {"defense": defense_pct, "production": production_pct}
        self.save_base(base_id, base)
        return f"{base_id}: power set defense={defense_pct}% production={production_pct}%"
    
    def set_defense(self, base_id: str, mode: str) -> str:
        base = self.get_base(base_id)
        if mode not in ("online", "offline", "overcharge"):
            return f"Invalid mode: {mode}. Use online/offline/overcharge"
        base["defense_status"] = mode
        self.save_base(base_id, base)
        return f"{base_id} defense: {mode}"

class Skill:
    def __init__(self):
        self.bm = BaseManager()
        self.commands = {
            "base_list": self.cmd_list,
            "base_info": self.cmd_info,
            "base_build": self.cmd_build,
            "base_upgrade": self.cmd_upgrade,
        }
    
    def cmd_list(self, *args):
        """base_list — show all bases."""
        bases = self.bm.list_bases()
        if not bases:
            return "No bases constructed."
        lines = ["ID       TYPE            ZONE    LVL  HP      POWER"]
        for b in bases:
            lines.append(f"{b['id']:8} {b['type']:15} {b['zone']:7} {b['level']:4} {b['health']:7} {b['power_use']:6}")
        return "\n".join(lines)
    
    def cmd_info(self, base_id: str, *args):
        """base_info <base_id> — detailed view."""
        try:
            b = self.bm.get_base(base_id)
            lines = [
                f"Base {base_id}: {b['building_type']} (Zone: {b['zone_id']})",
                f"Level: {b['level']} | Health: {b['health']} | Crew: {b.get('crew',0)}",
                f"Power use: {b.get('power_use',0)} | Status: {b.get('defense_status','unknown')}",
                f"Storage: {b.get('storage',{})}",
                f"Modules: {', '.join(b.get('modules',[]))}",
                f"Active projects: {', '.join(b.get('active_projects',[]))}",
            ]
            return "\n".join(lines)
        except FileNotFoundError:
            return f"Base {base_id} not found"
    
    def cmd_build(self, zone_id: str, building_type: str, *args):
        """base_build <zone_id> <building_type> [level] — construct new base."""
        level = int(args[0]) if args else 1
        return self.bm.construct(zone_id, building_type, level)
    
    def cmd_upgrade(self, base_id: str, to_level: str = "2", *args):
        """base_upgrade <base_id> [to_level] — upgrade building."""
        return self.bm.upgrade(base_id, int(to_level))
    
    def cmd_power(self, base_id: str, defense: str, production: str, *args):
        """base_power <base_id> <defense_pct> <production_pct> — allocate power."""
        return self.bm.set_power(base_id, int(defense), int(production))
    
    def cmd_defense(self, base_id: str, mode: str, *args):
        """base_defense <base_id> <mode> — set defense mode (online/offline/overcharge)."""
        return self.bm.set_defense(base_id, mode)
