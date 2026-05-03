"""Ship Management Skill — real implementation using actual mod schema."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import SHIP_MODIFIED
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import SHIP_MODIFIED

class ShipManager:
    """Manages all ships, loadouts, cargo transfers."""
    
    def __init__(self):
        self.ships_path = os.path.join(reg.config.get("mod_path", ""), "ships")
        self.manifest_path = os.path.join(self.ships_path, "manifest.json")
        
    def list_ships(self, filter_owner=None) -> List[Dict[str, Any]]:
        """List all ships with summary stats."""
        ships = []
        for f in os.listdir(self.ships_path):
            if f.startswith("ship_") and f.endswith(".json"):
                with open(os.path.join(self.ships_path, f)) as fp:
                    data = json.load(fp)
                if filter_owner and data.get("type") != filter_owner:
                    continue
                ships.append({
                    "id": data["id"],
                    "name": data["name"],
                    "type": data.get("type", "unknown"),
                    "speed": data.get("base_speed", 0),
                    "health": data.get("base_health", 0),
                    "equipped": list(data.get("equipped_parts", {}).keys()),
                    "modifiable": data.get("modifiable", False),
                })
        return ships
    
    def get_ship(self, ship_id: str) -> Dict[str, Any]:
        path = os.path.join(self.ships_path, f"{ship_id}.json")
        with open(path) as f:
            return json.load(f)
    
    def save_ship(self, ship_id: str, data: Dict[str, Any]):
        path = os.path.join(self.ships_path, f"{ship_id}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        reg.emit(SHIP_MODIFIED, ship_id=ship_id)
    
    def swap_part(self, ship_id: str, part_type: str, new_part: str) -> str:
        """Swap a single part (equipped_parts)."""
        ship = self.get_ship(ship_id)
        equipped = ship.setdefault("equipped_parts", {})
        if part_type not in equipped:
            return f"Error: {ship_id} has no {part_type} slot"
        old = equipped[part_type]
        equipped[part_type] = new_part
        self.save_ship(ship_id, ship)
        return f"Swapped {ship_id} {part_type}: {old} → {new_part}"
    
    def set_active(self, ship_id: str) -> str:
        """Set ship as active player vessel (in manifest)."""
        ship = self.get_ship(ship_id)
        if ship.get("type") != "player":
            return f"Error: {ship_id} is not a player ship"
        with open(self.manifest_path) as f:
            manifest = json.load(f)
        manifest["active_ship_id"] = ship_id
        manifest["player_ships"] = [ship_id]
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        return f"Active ship set to {ship['name']} ({ship_id})"

class Skill:
    def __init__(self):
        self.manager = ShipManager()
        self.commands = {
            "list": self.cmd_list,
            "info": self.cmd_info,
            "swap_part": self.cmd_swap_part,
            "set_active": self.cmd_set_active,
        }
    
    def cmd_list(self, *args):
        """ship list — show all ships."""
        ships = self.manager.list_ships()
        if not ships:
            return "No ships found."
        lines = [f"{'ID':8} {'NAME':25} {'TYPE':8} {'SPD':4} {'HP':5} {'PARTS'}"]
        for s in ships:
            parts = '/'.join(s['equipped'])
            lines.append(f"{s['id']:8} {s['name']:25} {s['type']:8} {s['speed']:4} {s['health']:5} {parts}")
        return "\n".join(lines)
    
    def cmd_info(self, ship_id: str, *args):
        """ship info <ship_id> — detailed loadout."""
        ship = self.manager.get_ship(ship_id)
        eq = ship.get("equipped_parts", {})
        av = ship.get("available_parts", {})
        lines = [
            f"Ship: {ship['name']} ({ship_id})",
            f"Type: {ship.get('type')} | Style: {ship.get('style')}",
            f"Base Speed: {ship.get('base_speed')} | Base Health: {ship.get('base_health')}",
            f"Modifiable: {ship.get('modifiable')}",
            f"Equipped:",
        ]
        for part_type, part_name in eq.items():
            avail = ', '.join(av.get(part_type, []))
            lines.append(f"  {part_type}: {part_name} (avail: {avail})")
        return "\n".join(lines)
    
    def cmd_swap_part(self, ship_id: str, part_type: str, new_part: str, *args):
        """ship swap_part <ship_id> <part_type> <new_part> — change equipped part."""
        return self.manager.swap_part(ship_id, part_type, new_part)
    
    def cmd_set_active(self, ship_id: str, *args):
        """ship set_active <ship_id> — set as active player vessel."""
        return self.manager.set_active(ship_id)
