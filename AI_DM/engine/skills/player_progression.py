"""Player Progression — XP, levels, achievements, perks."""
import json, os
from typing import Dict, List, Any
try:
    from ..registry import reg
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from registry import reg
try:
    from ..events import LEVEL_UP, ACHIEVEMENT_UNLOCKED
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from events import LEVEL_UP, ACHIEVEMENT_UNLOCKED

# Available perks
PERKS = {
    'strong': {'name': 'Strong', 'description': '+10 damage', 'required_level': 2},
    'tough': {'name': 'Tough', 'description': '+20 max HP', 'required_level': 3},
    'quick': {'name': 'Quick', 'description': '+10% speed (non-combat)', 'required_level': 5},
    'rich': {'name': 'Rich', 'description': '+10% credits from all sources', 'required_level': 10},
    'healer': {'name': 'Healer', 'description': 'Passive HP regeneration 1 HP per 10s', 'required_level': 8},
}

class ProgressionManager:
    """Handles XP, levels, skills, achievements."""
    
    SAVE_PATH = os.path.expanduser("~/HylianModding/AI_DM/current_state.json")
    
    def __init__(self):
        self.state = reg.player_state
        self.state.setdefault('perks', [])  # list of unlocked perk ids
        # XP curve: level N requires N * 100 XP total
        self.xp_table = {n: n * 100 for n in range(1, 101)}
    
    def add_xp(self, amount: int) -> str:
        self.state["xp"] = self.state.get("xp", 0) + amount
        leveled = []
        while self.state["xp"] >= self.state.get("xp_to_next", 100):
            self.state["level"] = self.state.get("level", 1) + 1
            self.state["xp"] -= self.state.get("xp_to_next", 100)
            self.state["xp_to_next"] = self.xp_table[self.state["level"]]
            self.state["max_hp"] = self.state.get("max_hp", 100) + 20
            self.state["current_hp"] = self.state["max_hp"]
            leveled.append(self.state["level"])
            reg.emit(LEVEL_UP, level=self.state["level"])
        if leveled:
            return f"Level up! Now Level {self.state['level']} (gained: {leveled})"
        return f"Gained {amount} XP. Total: {self.state['xp']}/{self.state['xp_to_next']}"
    
    def heal(self, amount: int) -> int:
        old = self.state.get("current_hp", 0)
        self.state["current_hp"] = min(self.state.get("max_hp", 100), old + amount)
        return self.state["current_hp"] - old
    
    def damage(self, amount: int) -> bool:
        self.state["current_hp"] = max(0, self.state.get("current_hp", 100) - amount)
        return self.state["current_hp"] > 0
    
    def unlock_achievement(self, ach_id: str, title: str) -> str:
        achieved = self.state.setdefault("achievements", [])
        if ach_id not in achieved:
            achieved.append(ach_id)
            reg.emit(ACHIEVEMENT_UNLOCKED, achievement_id=ach_id, title=title)
            return f"Achievement Unlocked: {title}!"
        return f"Achievement {ach_id} already unlocked"
    
    # ── Perks management ──
    def perks_list(self) -> str:
        """List all perks and their unlock status."""
        owned = set(self.state.get('perks', []))
        player_level = self.state.get('level', 1)
        lines = ["Available Perks:"]
        for pid, pinfo in PERKS.items():
            status = "UNLOCKED" if pid in owned else f"LOCKED (req Lv{pinfo['required_level']})"
            lines.append(f"  {pinfo['name']} ({pid}): {pinfo['description']} — {status}")
        return "\n".join(lines)
    
    def perks_assign(self, perk_id: str) -> str:
        """Assign a perk if eligible."""
        if perk_id not in PERKS:
            return f"Unknown perk: {perk_id}"
        if perk_id in self.state.get('perks', []):
            return f"Perk {perk_id} already assigned."
        req_lvl = PERKS[perk_id]['required_level']
        if self.state.get('level', 1) < req_lvl:
            return f"Requires level {req_lvl}. You are level {self.state.get('level',1)}."
        # Assign
        self.state.setdefault('perks', []).append(perk_id)
        # Apply immediate effect if any
        if perk_id == 'tough':
            self.state['max_hp'] = self.state.get('max_hp', 100) + 20
            self.state['current_hp'] = self.state.get('current_hp', 100) + 20
        elif perk_id == 'strong':
            # Could store a damage bonus; for simplicity just flag
            pass
        elif perk_id == 'rich':
            pass
        return f"Perk '{PERKS[perk_id]['name']}' assigned!"
    
    def status(self) -> str:
        s = self.state
        lines = [
            f"Level {s.get('level',1)} — XP {s.get('xp',0)}/{s.get('xp_to_next',100)}",
            f"HP {s.get('current_hp',0)}/{s.get('max_hp',100)} | Credits: {s.get('credits',0)}",
            f"Zones: {len(s.get('zones_visited',[]))} | Ships: {len(s.get('ships_owned',[]))}",
            f"Skills unlocked: {', '.join(s.get('skills_unlocked',[]))}",
            f"Perks: {', '.join(s.get('perks',[]))}",
        ]
        return "\n".join(lines)
    
    def save(self) -> str:
        with open(self.SAVE_PATH, 'w') as f:
            json.dump(self.state, f, indent=2)
        return f"Saved player state to {self.SAVE_PATH}"

class Skill:
    def __init__(self):
        self.pm = ProgressionManager()
        self.commands = {
            "xp": self.cmd_xp,
            "level": self.cmd_level,
            "heal": self.cmd_heal,
            "damage": self.cmd_damage,
            "status": self.cmd_status,
            "save": self.cmd_save,
            "achievement": self.cmd_achievement,
            "unlock": self.cmd_unlock,
            "perks": self.cmd_perks,
        }
    
    def cmd_xp(self, amount: str = "10", *args):
        """player xp [amount] — add XP."""
        return self.pm.add_xp(int(amount))
    
    def cmd_level(self, *args):
        """player level — show level info."""
        s = self.pm.state
        return f"Level {s.get('level',1)} | HP: {s.get('current_hp',0)}/{s.get('max_hp',100)} | XP: {s.get('xp',0)}/{s.get('xp_to_next',100)}"
    
    def cmd_heal(self, amount: str = "50", *args):
        """player heal [amount] — restore HP."""
        healed = self.pm.heal(int(amount))
        s = self.pm.state
        return f"Healed {healed} HP. Now {s['current_hp']}/{s['max_hp']}"
    
    def cmd_damage(self, amount: str = "10", *args):
        """player damage [amount] — take damage."""
        alive = self.pm.damage(int(amount))
        s = self.pm.state
        if not alive:
            return f" incapacitated! HP=0. Respawning at {s.get('current_zone','zone_0')}..."
        return f"Took {amount} damage. HP {s['current_hp']}/{s['max_hp']}"
    
    def cmd_status(self, *args):
        """player status — full status."""
        return self.pm.status()
    
    def cmd_save(self, *args):
        """player save — persist."""
        return self.pm.save()
    
    def cmd_achievement(self, *args):
        """achievements — list all."""
        ach = self.pm.state.get("achievements", [])
        return f"Achievements unlocked: {', '.join(ach) if ach else 'none'}"
    
    def cmd_unlock(self, ach_id: str, title: str = "Custom Achievement", *args):
        """achievement_unlock <id> <title> — manually unlock."""
        return self.pm.unlock_achievement(ach_id, title)
    
    def cmd_perks(self, action: str = None, perk_id: str = None, *args):
        """perks [list|assign <perk_id>] — manage perks."""
        if action is None or action == 'list':
            return self.pm.perks_list()
        elif action == 'assign':
            if not perk_id:
                return "Usage: perks assign <perk_id>"
            return self.pm.perks_assign(perk_id)
        else:
            return f"Unknown perks action: {action}. Use 'list' or 'assign'."
