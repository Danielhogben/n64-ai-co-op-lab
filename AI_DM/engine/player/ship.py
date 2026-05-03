"""Active ship tracking, cargo hold, part inventory."""
import json, os
from typing import Dict, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from registry import reg

class ActiveShip:
    """Tracks the player's currently active ship and cargo."""
    
    SHIPS_PATH = os.path.join(reg.config.get("mod_path", ""), "ships")
    MANIFEST = os.path.join(SHIPS_PATH, "manifest.json")
    
    def __init__(self):
        self.active_id = None
        self.cargo = []  # list of {item_id, quantity}
        self._load()
    
    def _load(self):
        if os.path.exists(self.MANIFEST):
            with open(self.MANIFEST) as f:
                m = json.load(f)
            self.active_id = m.get("active_ship_id")
        if not self.active_id:
            # Default to first player ship in manifest or ship_0
            self.active_id = "ship_0"
    
    def get_active(self) -> Dict[str, Any]:
        path = os.path.join(self.SHIPS_PATH, f"{self.active_id}.json")
        with open(path) as f:
            return json.load(f)
    
    def set_active(self, ship_id: str) -> str:
        ship_path = os.path.join(self.SHIPS_PATH, f"{ship_id}.json")
        if not os.path.exists(ship_path):
            return f"Ship {ship_id} not found"
        with open(ship_path) as f:
            data = json.load(f)
        if data.get("type") != "player":
            return f"Error: {ship_id} is not a player ship"
        # Update manifest
        with open(self.MANIFEST) as f:
            m = json.load(f)
        m["active_ship_id"] = ship_id
        with open(self.MANIFEST, 'w') as f:
            json.dump(m, f, indent=2)
        self.active_id = ship_id
        return f"Active ship set to {data['name']} ({ship_id})"
    
    def cargo_add(self, item_id: str, qty: int = 1) -> str:
        """Add item to ship cargo hold."""
        # Find existing stack
        for item in self.cargo:
            if item["item_id"] == item_id:
                item["quantity"] += qty
                return f"Cargo: {item_id} now {item['quantity']}"
        self.cargo.append({"item_id": item_id, "quantity": qty})
        return f"Cargo: added {qty}x {item_id}"
    
    def cargo_remove(self, item_id: str, qty: int = 1) -> str:
        for item in self.cargo:
            if item["item_id"] == item_id:
                if item["quantity"] < qty:
                    return f"Insufficient cargo: have {item['quantity']}, need {qty}"
                item["quantity"] -= qty
                if item["quantity"] <= 0:
                    self.cargo.remove(item)
                return f"Cargo: removed {qty}x {item_id}"
        return f"Item {item_id} not in cargo"
    
    def cargo_list(self) -> str:
        if not self.cargo:
            return "Cargo hold empty."
        lines = [f"{'Item':20} {'Qty':>5}"]
        for item in self.cargo:
            lines.append(f"{item['item_id']:20} {item['quantity']:5}")
        return "\n".join(lines)

class Skill:
    """Ship management skill for active ship and cargo."""
    def __init__(self):
        self.ship = ActiveShip()
        self.commands = {
            "active": self.cmd_active,
            "set_active": self.cmd_set_active,
            "cargo": self.cmd_cargo,
            "cargo_add": self.cmd_cargo_add,
            "cargo_remove": self.cmd_cargo_remove,
            "info": self.cmd_info,
        }
    
    def cmd_active(self, *args):
        """ship active — show current active ship."""
        ship = self.ship.get_active()
        return f"Active: {ship['name']} ({self.ship.active_id})\nSpeed: {ship.get('base_speed')} | HP: {ship.get('base_health')}"
    
    def cmd_set_active(self, ship_id: str, *args):
        """ship set_active <ship_id> — switch active ship."""
        return self.ship.set_active(ship_id)
    
    def cmd_info(self, *args):
        """ship info — detailed view of active ship."""
        ship = self.ship.get_active()
        eq = ship.get("equipped_parts", {})
        lines = [f"{ship['name']} ({self.ship.active_id})", f"Type: {ship.get('type')} | Style: {ship.get('style')}"]
        for pt, pn in eq.items():
            lines.append(f"  {pt}: {pn}")
        return "\n".join(lines)
    
    def cmd_cargo(self, *args):
        """ship cargo — list cargo hold contents."""
        return self.ship.cargo_list()
    
    def cmd_cargo_add(self, item_id: str, qty: str = "1", *args):
        """ship cargo_add <item_id> [qty] — add cargo."""
        return self.ship.cargo_add(item_id, int(qty))
    
    def cmd_cargo_remove(self, item_id: str, qty: str = "1", *args):
        """ship cargo_remove <item_id> [qty] — remove cargo."""
        return self.ship.cargo_remove(item_id, int(qty))
