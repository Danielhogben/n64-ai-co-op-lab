"""Player state management: tracks level, HP, XP, current zone, credits."""
import json, os
from typing import Dict, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from registry import reg

class PlayerState:
    """Handles player progression, stats, and persistence."""
    
    SAVE_PATH = os.path.expanduser("~/HylianModding/AI_DM/current_state.json")
    
    def __init__(self):
        self.state = reg.player_state if reg.player_state else self._default_state()
        # XP thresholds: level N requires N * 100 XP
        self.xp_table = {n: n * 100 for n in range(1, 101)}
    
    def _default_state(self) -> Dict[str, Any]:
        return {
            "level": 1,
            "xp": 0,
            "xp_to_next": 100,
            "current_hp": 100,
            "max_hp": 100,
            "current_zone": "zone_0",
            "credits": 1000,
            "zones_visited": ["zone_0"],
            "ships_owned": ["ship_0"],
            "perks_unlocked": [],
            "achievements": [],
            "inventory": {"slots_total": 30, "slots_used": 0, "items": []},
        }
    
    def add_xp(self, amount: int) -> Dict[str, Any]:
        """Add XP and handle level-ups."""
        self.state["xp"] += amount
        leveled = []
        while self.state["xp"] >= self.state["xp_to_next"]:
            self.state["level"] += 1
            self.state["xp"] -= self.state["xp_to_next"]
            self.state["xp_to_next"] = self.xp_table[self.state["level"]]
            # Stat increases
            self.state["max_hp"] += 20
            self.state["current_hp"] = self.state["max_hp"]
            leveled.append(self.state["level"])
            reg.emit("player.levelup", level=self.state["level"])
        return {"new_level": self.state["level"], "levels_gained": leveled}
    
    def heal(self, amount: int) -> int:
        """Heal HP, returns amount actually healed."""
        old = self.state["current_hp"]
        self.state["current_hp"] = min(self.state["max_hp"], self.state["current_hp"] + amount)
        return self.state["current_hp"] - old
    
    def damage(self, amount: int) -> bool:
        """Apply damage, returns True if still alive."""
        self.state["current_hp"] -= amount
        if self.state["current_hp"] <= 0:
            self.state["current_hp"] = 0
            return False
        return True
    
    def set_zone(self, zone_id: str):
        self.state["current_zone"] = zone_id
        if zone_id not in self.state["zones_visited"]:
            self.state["zones_visited"].append(zone_id)
    
    def add_credits(self, amount: int) -> int:
        self.state["credits"] += amount
        return self.state["credits"]
    
    def save(self):
        reg.player_state = self.state
        with open(self.SAVE_PATH, 'w') as f:
            json.dump(self.state, f, indent=2)
        return f"Saved to {self.SAVE_PATH}"
    
    def to_dict(self) -> Dict[str, Any]:
        return dict(self.state)

class Skill:
    """Player progression skill — handles XP and level-ups."""
    def __init__(self):
        self.ps = PlayerState()
        self.commands = {
            "xp": self.cmd_xp,
            "level": self.cmd_level,
            "heal": self.cmd_heal,
            "damage": self.cmd_damage,
            "save": self.cmd_save,
            "status": self.cmd_status,
        }
        self.hooks = {}
    
    def cmd_xp(self, amount: str = "10", *args):
        """player xp [amount] — add XP (default 10)."""
        amt = int(amount)
        res = self.ps.add_xp(amt)
        if res["levels_gained"]:
            return f"Level up! Now level {res['new_level']} (gained: {res['levels_gained']})"
        return f"Gained {amt} XP. Total: {self.ps.state['xp']}/{self.ps.state['xp_to_next']}"
    
    def cmd_level(self, *args):
        """player level — show current level and stats."""
        s = self.ps.state
        return f"Level {s['level']} | HP: {s['current_hp']}/{s['max_hp']} | XP: {s['xp']}/{s['xp_to_next']}"
    
    def cmd_heal(self, amount: str = "50", *args):
        """player heal [amount] — restore HP."""
        amt = int(amount)
        healed = self.ps.heal(amt)
        return f"Healed {healed} HP. Now {self.ps.state['current_hp']}/{self.ps.state['max_hp']}"
    
    def cmd_damage(self, amount: str = "10", *args):
        """player damage [amount] — take damage."""
        amt = int(amount)
        alive = self.ps.damage(amt)
        if not alive:
            return f" incapacitated! HP=0. Respawning at zone {self.ps.state['current_zone']}..."
        return f"Took {amt} damage. HP {self.ps.state['current_hp']}/{self.ps.state['max_hp']}"
    
    def cmd_save(self, *args):
        """player save — persist state to disk."""
        return self.ps.save()
    
    def cmd_status(self, *args):
        """player status — full status report."""
        s = self.ps.state
        lines = [
            f"Level {s['level']} XP {s['xp']}/{s['xp_to_next']}",
            f"HP {s['current_hp']}/{s['max_hp']} | Credits: {s['credits']}",
            f"Zone: {s['current_zone']} | Zones visited: {len(s['zones_visited'])}",
            f"Ships: {len(s['ships_owned'])} | Perks: {len(s['perks_unlocked'])}",
        ]
        return "\n".join(lines)
