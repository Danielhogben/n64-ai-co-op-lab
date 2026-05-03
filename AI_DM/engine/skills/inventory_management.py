"""Inventory Management — item tracking, transfers, stack management."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg

class InventoryManager:
    """Manages player inventory, ship cargo, base storage."""
    
    def __init__(self):
        self.state = reg.player_state
        self.inv = self.state.setdefault("inventory", {"slots_total": 30, "slots_used": 0, "items": []})
        self.mod_path = reg.config.get("mod_path", "")
    
    def list_items(self, location: str = "player") -> List[Dict[str, Any]]:
        if location == "player":
            return self.inv.get("items", [])
        # For ship or base, read from respective JSONs
        return []
    
    def add(self, item_id: str, quantity: int = 1) -> str:
        items = self.inv.setdefault("items", [])
        existing = next((i for i in items if i["item_id"] == item_id), None)
        if existing:
            existing["quantity"] += quantity
            return f"Added {quantity}x {item_id} (total: {existing['quantity']})"
        if self.inv["slots_used"] >= self.inv["slots_total"]:
            return "Inventory full"
        items.append({"item_id": item_id, "quantity": quantity})
        self.inv["slots_used"] += 1
        reg.emit("item.pickup", item_id=item_id, quantity=quantity)
        return f"Added {quantity}x {item_id} to slot {self.inv['slots_used']}"
    
    def remove(self, item_id: str, quantity: int = 1) -> str:
        items = self.inv["items"]
        for i, it in enumerate(items):
            if it["item_id"] == item_id:
                if it["quantity"] < quantity:
                    return f"Insufficient: have {it['quantity']}, need {quantity}"
                it["quantity"] -= quantity
                if it["quantity"] <= 0:
                    items.pop(i)
                    self.inv["slots_used"] -= 1
                return f"Removed {quantity}x {item_id}"
        return f"Item {item_id} not found"
    
    def has(self, item_id: str, quantity: int = 1) -> bool:
        it = next((i for i in self.inv.get("items", []) if i["item_id"] == item_id), None)
        return it and it["quantity"] >= quantity
    
    def count(self, item_id: str) -> int:
        it = next((i for i in self.inv.get("items", []) if i["item_id"] == item_id), None)
        return it["quantity"] if it else 0
    
    def transfer_to_ship(self, ship_id: str, item_id: str, quantity: int) -> str:
        if not self.has(item_id, quantity):
            return f"Cannot transfer — only have {self.count(item_id)}x {item_id}"
        # Load ship
        ship_path = os.path.join(self.mod_path, "ships", f"{ship_id}.json")
        if not os.path.exists(ship_path):
            return f"Ship {ship_id} not found"
        with open(ship_path) as f:
            ship = json.load(f)
        # Init cargo
        cargo = ship.setdefault("cargo_loaded", [])
        existing = next((c for c in cargo if c["item_id"] == item_id), None)
        if existing:
            existing["quantity"] += quantity
        else:
            cargo.append({"item_id": item_id, "quantity": quantity})
        self.remove(item_id, quantity)
        with open(ship_path, 'w') as f:
            json.dump(ship, f, indent=2)
        return f"Transferred {quantity}x {item_id} to ship {ship_id}"
    
    def transfer_to_base(self, base_id: str, item_id: str, quantity: int) -> str:
        # Similar to ship transfer but to base storage
        base_path = os.path.join(self.mod_path, "base_building", f"{base_id}.json")
        if not os.path.exists(base_path):
            return f"Base {base_id} not found"
        if not self.has(item_id, quantity):
            return f"Insufficient items"
        with open(base_path) as f:
            base = json.load(f)
        storage = base.setdefault("storage", {"items": {}})
        items_dict = storage.setdefault("items", {})
        items_dict[item_id] = items_dict.get(item_id, 0) + quantity
        self.remove(item_id, quantity)
        with open(base_path, 'w') as f:
            json.dump(base, f, indent=2)
        return f"Transferred {quantity}x {item_id} to base {base_id}"

class Skill:
    def __init__(self):
        self.im = InventoryManager()
        self.commands = {
            "list": self.cmd_list,
            "show": self.cmd_list,
            "add": self.cmd_add,
            "remove": self.cmd_remove,
            "has": self.cmd_has,
            "count": self.cmd_count,
            "transfer": self.cmd_transfer,
            "to_ship": self.cmd_to_ship,
            "to_base": self.cmd_to_base,
        }
    
    def cmd_list(self, *args):
        """inv_list — show inventory."""
        items = self.im.list_items()
        if not items:
            return "Inventory empty"
        lines = [f"{'Slot':5} {'Item':20} {'Qty':>5}"]
        for i, it in enumerate(items, 1):
            lines.append(f"{i:5} {it['item_id']:20} {it['quantity']:5}")
        return "\n".join(lines)
    
    def cmd_add(self, item_id: str, quantity: str = "1", *args):
        """inv_add <item_id> [qty] — add item."""
        return self.im.add(item_id, int(quantity))
    
    def cmd_remove(self, item_id: str, quantity: str = "1", *args):
        """inv_remove <item_id> [qty] — remove item."""
        return self.im.remove(item_id, int(quantity))
    
    def cmd_has(self, item_id: str, quantity: str = "1", *args):
        """inv_has <item_id> [qty] — check."""
        return f"Has {self.im.count(item_id)}x {item_id}: {self.im.has(item_id, int(quantity))}"
    
    def cmd_count(self, item_id: str, *args):
        """inv_count <item_id> — count specific."""
        return f"{item_id}: {self.im.count(item_id)}"
    
    def cmd_transfer(self, item_id: str, quantity: str, target: str, *args):
        """inv_transfer <item_id> <qty> <target> — transfer (target=base_X or ship_X)."""
        qty = int(quantity)
        if target.startswith("ship_"):
            return self.im.transfer_to_ship(target, item_id, qty)
        elif target.startswith("base_"):
            return self.im.transfer_to_base(target, item_id, qty)
        else:
            return f"Invalid target {target}. Use base_<id> or ship_<id>"
    
    def cmd_to_ship(self, ship_id: str, item_id: str, quantity: str = "1", *args):
        """inv_to_ship <ship_id> <item_id> [qty] — direct to ship."""
        return self.im.transfer_to_ship(ship_id, item_id, int(quantity))
    
    def cmd_to_base(self, base_id: str, item_id: str, quantity: str = "1", *args):
        """inv_to_base <base_id> <item_id> [qty] — direct to base."""
        return self.im.transfer_to_base(base_id, item_id, int(quantity))
