"""Loot crates, drops, and rare items."""
import random
from ursina import *

LOOT_TABLE = {
    'common': [
        {'type': 'credits', 'min': 10, 'max': 50},
        {'type': 'minerals', 'min': 5, 'max': 15},
        {'type': 'ammo', 'min': 5, 'max': 15},
    ],
    'uncommon': [
        {'type': 'credits', 'min': 50, 'max': 150},
        {'type': 'minerals', 'min': 20, 'max': 50},
        {'type': 'heal', 'min': 20, 'max': 40},
        {'type': 'weapon_unlock', 'choices': ['rifle', 'shotgun']},
    ],
    'rare': [
        {'type': 'credits', 'min': 200, 'max': 500},
        {'type': 'weapon_unlock', 'choices': ['sniper', 'rocket', 'minigun']},
        {'type': 'skill_point', 'min': 1, 'max': 2},
        {'type': 'max_hp', 'min': 10, 'max': 30},
    ],
    'legendary': [
        {'type': 'credits', 'min': 1000, 'max': 5000},
        {'type': 'weapon_upgrade', 'min': 1, 'max': 3},
        {'type': 'skill_point', 'min': 3, 'max': 5},
        {'type': 'companion', 'min': 1, 'max': 1},
    ],
}

class LootCrate(Entity):
    def __init__(self, pos, rarity='common'):
        colors = {'common': color.gray, 'uncommon': color.green, 'rare': color.blue, 'legendary': color.gold}
        super().__init__(
            model='cube',
            color=colors.get(rarity, color.white),
            position=pos,
            scale=(0.8, 0.8, 0.8),
            collider='box'
        )
        self.rarity = rarity
        self.opened = False
        self.glow = Entity(model='sphere', color=colors.get(rarity, color.white), scale=1.5, position=pos, alpha=0.3)

    def open(self, player, hud, weapon_sys, skill_tree):
        if self.opened:
            return "Already opened."
        self.opened = True
        destroy(self.glow)
        self.color = color.dark_gray
        self.scale = (0.6, 0.2, 0.6)

        rewards = []
        table = LOOT_TABLE.get(self.rarity, LOOT_TABLE['common'])
        for _ in range(random.randint(1, 3)):
            item = random.choice(table)
            rtype = item['type']
            if rtype == 'credits':
                amount = random.randint(item['min'], item['max'])
                player.credits += amount
                rewards.append(f"{amount} CR")
            elif rtype == 'minerals':
                amount = random.randint(item['min'], item['max'])
                player.minerals += amount
                rewards.append(f"{amount} minerals")
            elif rtype == 'ammo':
                amount = random.randint(item['min'], item['max'])
                weapon_sys.add_ammo(weapon_sys.current, amount)
                rewards.append(f"{amount} ammo")
            elif rtype == 'heal':
                amount = random.randint(item['min'], item['max'])
                player.hp = min(player.max_hp, player.hp + amount)
                rewards.append(f"+{amount} HP")
            elif rtype == 'weapon_unlock':
                w = random.choice(item['choices'])
                weapon_sys.unlock(w)
                rewards.append(f"Unlocked {w}!")
            elif rtype == 'skill_point':
                amount = random.randint(item['min'], item['max'])
                skill_tree.add_points(amount)
                rewards.append(f"+{amount} skill points!")
            elif rtype == 'max_hp':
                amount = random.randint(item['min'], item['max'])
                player.max_hp += amount
                rewards.append(f"+{amount} max HP")
            elif rtype == 'weapon_upgrade':
                rewards.append(weapon_sys.upgrade(weapon_sys.current) or "Upgrade failed")
            elif rtype == 'companion':
                rewards.append("New companion acquired!")

        hud.set_message(f"LOOT ({self.rarity.upper()}): {', '.join(rewards)}")
        return f"Opened {self.rarity} crate!"


class LootManager:
    def __init__(self):
        self.crates = []

    def spawn_crates(self, center, count=10, radius=100):
        for _ in range(count):
            pos = center + Vec3(random.uniform(-radius, radius), 3, random.uniform(-radius, radius))
            r = random.choices(['common', 'uncommon', 'rare', 'legendary'], weights=[60, 25, 12, 3])[0]
            crate = LootCrate(pos, r)
            self.crates.append(crate)

    def check_nearby(self, player, hud, weapon_sys, skill_tree):
        for crate in self.crates:
            if not crate.opened and distance(crate.position, player.position) < 3:
                crate.open(player, hud, weapon_sys, skill_tree)
