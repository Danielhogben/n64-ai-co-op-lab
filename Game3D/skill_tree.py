"""Skill tree and perk system."""
from ursina import *

SKILLS = {
    'health_boost': {'name': 'Vitality', 'max': 5, 'cost': 1, 'desc': '+20 Max HP per rank'},
    'damage_boost': {'name': 'Weapon Mastery', 'max': 5, 'cost': 1, 'desc': '+10% damage per rank'},
    'speed_boost': {'name': 'Agility', 'max': 5, 'cost': 1, 'desc': '+1 move speed per rank'},
    'mining_boost': {'name': 'Geologist', 'max': 3, 'cost': 1, 'desc': '+50% mineral yield'},
    'scan_boost': {'name': 'Deep Scan', 'max': 3, 'cost': 1, 'desc': 'Discover 2 ROMs per scan'},
    'craft_boost': {'name': 'Engineer', 'max': 3, 'cost': 1, 'desc': 'Crafting costs -20% per rank'},
    'luck': {'name': 'Lucky Find', 'max': 5, 'cost': 1, 'desc': '+10% rare loot chance'},
    'regen': {'name': 'Auto-Repair', 'max': 3, 'cost': 2, 'desc': 'HP regen +1/s per rank'},
    'crit': {'name': 'Critical Strikes', 'max': 5, 'cost': 1, 'desc': '+5% crit chance per rank'},
    'dash': {'name': 'Void Dash', 'max': 1, 'cost': 3, 'desc': 'Double-tap direction to dash'},
}

class SkillTree:
    def __init__(self, player):
        self.player = player
        self.points = 0
        self.ranks = {k: 0 for k in SKILLS}
        self.apply_bonuses()

    def add_points(self, n):
        self.points += n

    def can_buy(self, key):
        if key not in SKILLS:
            return False
        s = SKILLS[key]
        return self.points >= s['cost'] and self.ranks[key] < s['max']

    def buy(self, key):
        if not self.can_buy(key):
            return None
        s = SKILLS[key]
        self.points -= s['cost']
        self.ranks[key] += 1
        self.apply_bonuses()
        return f"{s['name']} rank {self.ranks[key]}!"

    def apply_bonuses(self):
        # Reset base stats before applying
        self.player.max_hp = 100 + self.ranks['health_boost'] * 20
        self.player.speed = 6 + self.ranks['speed_boost']
        # Damage multiplier applied in weapon system
        # Mining, scan, craft, luck, regen, crit handled elsewhere

    def get_menu_lines(self):
        lines = [f"SKILL POINTS: {self.points}", ""]
        for key, s in SKILLS.items():
            r = self.ranks[key]
            status = f"[{r}/{s['max']}]" if r < s['max'] else "[MAX]"
            lines.append(f"{key}: {s['name']} {status} — {s['desc']} (Cost: {s['cost']})")
        return lines
