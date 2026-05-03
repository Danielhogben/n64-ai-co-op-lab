"""Economy System — credits, markets, trading routes."""
import json, os, random
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg

class EconomyManager:
    """Manages player credits, market prices, and basic trading."""
    
    def __init__(self):
        self.state = reg.player_state
        self.state.setdefault("credits", 1000)
        self.markets: Dict[str, Dict] = {} # zone_id -> items
    
    def get_credits(self) -> int:
        return self.state.get("credits", 0)
    
    def add_credits(self, amount: int) -> int:
        self.state["credits"] = self.state.get("credits", 0) + amount
        return self.state["credits"]
    
    def list_market(self, zone_id: str = None) -> str:
        if not zone_id:
            zone_id = self.state.get("current_zone", "zone_0")
        
        # Simple procedural market if not exists
        if zone_id not in self.markets:
            self.markets[zone_id] = {
                "fuel": {"buy": 10, "sell": 8, "qty": random.randint(50, 200)},
                "metal_ore": {"buy": 50, "sell": 40, "qty": random.randint(10, 50)},
                "crystal_ore": {"buy": 150, "sell": 120, "qty": random.randint(5, 15)},
                "ration_pack": {"buy": 5, "sell": 4, "qty": 100},
            }
        
        market = self.markets[zone_id]
        lines = [f"Market at {zone_id}:", f"{'Item':15} {'Buy':>5} {'Sell':>5} {'Qty':>5}"]
        for item, prices in market.items():
            lines.append(f"{item:15} {prices['buy']:5} {prices['sell']:5} {prices['qty']:5}")
        return "\n".join(lines)

    def buy(self, item_id: str, quantity: int = 1) -> str:
        zone_id = self.state.get("current_zone", "zone_0")
        market = self.markets.get(zone_id)
        if not market:
            # Force generation
            self.list_market(zone_id)
            market = self.markets.get(zone_id)
            
        if item_id not in market:
            return f"Item {item_id} not available at this market."
        
        prices = market[item_id]
        if prices['qty'] < quantity:
            return f"Insufficient stock: only {prices['qty']} available."
        
        total_cost = prices['buy'] * quantity
        if self.state["credits"] < total_cost:
            return f"Insufficient credits: need {total_cost}, have {self.state['credits']}."
        
        # Deduct credits
        self.state["credits"] -= total_cost
        prices['qty'] -= quantity
        
        # Emit event for inventory management to pick up
        reg.emit("item.pickup", item_id=item_id, quantity=quantity, source="market")
        
        return f"Bought {quantity}x {item_id} for {total_cost} credits. Remaining: {self.state['credits']}"

class Skill:
    def __init__(self):
        self.em = EconomyManager()
        self.commands = {
            "market_list": self.cmd_market_list,
            "buy": self.cmd_buy,
            "credits": self.cmd_credits,
            "add_credits": self.cmd_add_credits,
        }
    
    def cmd_market_list(self, zone_id: str = None, *args):
        """economy market_list [zone_id] — show local market."""
        return self.em.list_market(zone_id)
    
    def cmd_buy(self, item_id: str, quantity: str = "1", *args):
        """economy buy <item_id> [qty] — buy from market."""
        try:
            qty = int(quantity)
        except ValueError:
            return f"Invalid quantity: {quantity}"
        return self.em.buy(item_id, qty)
    
    def cmd_credits(self, *args):
        """economy credits — show current credits."""
        return f"Credits: {self.em.get_credits()}"

    def cmd_add_credits(self, amount: str, *args):
        """economy add_credits <amount> — debug add credits."""
        try:
            amt = int(amount)
        except ValueError:
            return f"Invalid amount: {amount}"
        new_total = self.em.add_credits(amt)
        return f"Added {amt} credits. New total: {new_total}"
