"""Reputation System — manage faction standings and social consequences."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import FACTION_REP_CHANGE
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import FACTION_REP_CHANGE

FACTIONS = [
    "Hylian Federation",
    "Gerudo Syndicate",
    "Goron Mining Corp",
    "Zora Oceanic Collective",
    "Sheikah Intelligence"
]

class ReputationManager:
    """Handles faction reputation, levels, and locks/unlocks."""
    
    def __init__(self):
        self.state = reg.player_state
        self.reps = self.state.setdefault("factions", {f: 0 for f in FACTIONS})
    
    def add_rep(self, faction: str, amount: int) -> str:
        if faction not in self.reps:
            # Try fuzzy match
            matching = [f for f in self.reps if faction.lower() in f.lower()]
            if matching:
                faction = matching[0]
            else:
                self.reps[faction] = 0
        
        old_val = self.reps[faction]
        new_val = old_val + amount
        self.reps[faction] = new_val
        
        reg.emit(FACTION_REP_CHANGE, faction=faction, amount=amount, total=new_val)
        
        # Check for rank changes (simple 100 pt increments)
        old_rank = old_val // 100
        new_rank = new_val // 100
        if new_rank > old_rank:
            return f"Reputation with {faction} increased to Rank {new_rank}! ({new_val})"
        elif new_rank < old_rank:
            return f"Reputation with {faction} decreased to Rank {new_rank}. ({new_val})"
        return f"Reputation with {faction} changed by {amount}. Total: {new_val}"

    def get_standing(self, faction: str) -> str:
        val = self.reps.get(faction, 0)
        if val >= 500: return "Exalted"
        if val >= 300: return "Revered"
        if val >= 100: return "Honored"
        if val >= 0: return "Neutral"
        if val >= -100: return "Unfriendly"
        if val >= -300: return "Hostile"
        return "Hated"

    def list_all(self) -> str:
        lines = ["Faction Standings:"]
        for f, val in self.reps.items():
            standing = self.get_standing(f)
            lines.append(f"  {f:25}: {val:4} ({standing})")
        return "\n".join(lines)

class Skill:
    def __init__(self):
        self.rm = ReputationManager()
        self.commands = {
            "list": self.cmd_list,
            "add": self.cmd_add,
            "set": self.cmd_set,
            "status": self.cmd_list,
        }
    
    def cmd_list(self, *args):
        """reputation list — show standings."""
        return self.rm.list_all()
    
    def cmd_add(self, faction: str, amount: str = "10", *args):
        """reputation add <faction> <amount> — modify rep."""
        try:
            amt = int(amount)
        except ValueError:
            return f"Invalid amount: {amount}"
        return self.rm.add_rep(faction, amt)
    
    def cmd_set(self, faction: str, amount: str, *args):
        """reputation set <faction> <amount> — debug set rep."""
        try:
            amt = int(amount)
        except ValueError:
            return f"Invalid amount: {amount}"
        if faction not in self.rm.reps:
             # Try fuzzy match
            matching = [f for f in self.rm.reps if faction.lower() in f.lower()]
            if matching:
                faction = matching[0]
        self.rm.reps[faction] = amt
        return f"Set {faction} reputation to {amt}."
