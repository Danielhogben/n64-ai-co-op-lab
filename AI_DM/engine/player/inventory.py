"""Inventory management: 30 slots, stacking, weight, item transfers."""
import json, os
from typing import Dict, List, Any, Optional
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from registry import reg

ITEM_DB_PATH = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods/ai_full_universe/items")

class Inventory:
    """Player inventory — add, remove, transfer items."""
    
    MAX_SLOTS = 30
    
    def __init__(self):
        self.inv = reg.player_state.setdefault("inventory", {"slots_total": 30, "slots_used": 0, "items": []})
    
    def _find_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        for it in self.inv["items"]:
            if it["item_id"] == item_id:
                return it
        return None
    
    def add(self, item_id: str, quantity: int = 1, metadata: Dict = None) -> Dict[str, Any]:
        """Add item to inventory. Returns result dict."""
        existing = self._find_item(item_id)
        if existing:
            existing["quantity"] += quantity
            return {"action": "stacked", "item_id": item_id, "new_qty": existing["quantity"]}
        # Require free slot
        if self.inv["slots_used"] >= self.MAX_SLOTS:
            return {"action": "fail", "error": "inventory full"}
        slot = {"item_id": item_id, "quantity": quantity}
        if metadata:
            slot.update(metadata)
        self.inv["items"].append(slot)
        self.inv["slots_used"] += 1
        return {"action": "added", "item_id": item_id, "quantity": quantity, "slots_used": self.inv["slots_used"]}
    
    def remove(self, item_id: str, quantity: int = 1) -> Dict[str, Any]:
        item = self._find_item(item_id)
        if not item:
            return {"action": "fail", "error": "item not found"}
        if item["quantity"] < quantity:
            return {"action": "fail", "error": "insufficient quantity"}
        item["quantity"] -= quantity
        if item["quantity"] <= 0:
            self.inv["items"].remove(item)
            self.inv["slots_used"] -= 1
        return {"action": "removed", "item_id": item_id, "remaining": item.get("quantity", 0)}
    
    def has(self, item_id: str, quantity: int = 1) -> bool:
        item = self._find_item(item_id)
        return item and item["quantity"] >= quantity
    
    def count(self, item_id: str) -> int:
        item = self._find_item(item_id)
        return item["quantity"] if item else 0
    
    def list_items(self) -> List[Dict[str, Any]]:
        return list(self.inv["items"])
    
    def transfer(self, item_id: str, quantity: int, target: str) -> str:
        # Transfer to base storage (stub)
        if not self.has(item_id, quantity):
            return "Cannot transfer — insufficient items"
        self.remove(item_id, quantity)
        return f"Transferred {quantity}x {item_id} to {target}"
    
    def clear(self):
        self.inv["items"] = []
        self.inv["slots_used"] = 0

class Skill:
    """inventory commands: show, add, remove, transfer."""
    def __init__(self):
        self.inv = Inventory()
        self.commands = {
            "show": self.cmd_show,
            "add": self.cmd_add,
            "remove": self.cmd_remove,
            "has": self.cmd_has,
            "transfer": self.cmd_transfer,
            "clear": self.cmd_clear,
        }
        self.hooks = {}
    
    def cmd_show(self, *args):
        """inv_show — display inventory contents."""
        items = self.inv.list_items()
        if not items:
            return "Inventory empty."
        lines = [f"Slot  Item ID               Qty"]
        for i, it in enumerate(items, 1):
            lines.append(f"{i:5} {it['item_id']:22} {it['quantity']:4}")
        return "\n".join(lines)
    
    def cmd_add(self, item_id: str, quantity: str = "1", *args):
        """inv_add <item_id> [quantity] — add item."""
        qty = int(quantity)
        res = self.inv.add(item_id, qty)
        if res["action"] == "added":
            return f"Added {qty}x {item_id} (slot {res['slots_used']})"
        elif res["action"] == "stacked":
            return f"Stacked into existing: now {res['new_qty']}x {item_id}"
        else:
            return f"Error: {res['error']}"
    
    def cmd_remove(self, item_id: str, quantity: str = "1", *args):
        """inv_remove <item_id> [quantity] — remove item."""
        qty = int(quantity)
        res = self.inv.remove(item_id, qty)
        if res["action"] == "removed":
            return f"Removed {qty}x {item_id}. Remaining: {res.get('remaining',0)}"
        else:
            return f"Error: {res['error']}"
    
    def cmd_has(self, item_id: str, quantity: str = "1", *args):
        """inv_has <item_id> [quantity] — check if owned."""
        qty = int(quantity)
        return f"Has {self.inv.count(item_id)}x {item_id} (need {qty}): {self.inv.has(item_id, qty)}"
    
    def cmd_transfer(self, item_id: str, quantity: str, target: str, *args):
        """inv_transfer <item_id> <qty> <target> — move to base storage."""
        qty = int(quantity)
        return self.inv.transfer(item_id, qty, target)
    
    def cmd_clear(self, *args):
        """inv_clear — empty inventory (danger)."""
        self.inv.clear()
        return "Inventory cleared."
