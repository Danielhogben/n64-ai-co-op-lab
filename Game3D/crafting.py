"""Crafting system with recipes and materials."""
from ursina import *

RECIPES = {
    'health_pack': {'name': 'Health Pack', 'minerals': 10, 'credits': 20, 'result': 'heal', 'value': 40},
    'armor_plate': {'name': 'Armor Plate', 'minerals': 30, 'credits': 50, 'result': 'max_hp', 'value': 25},
    'ammo_box': {'name': 'Ammo Box', 'minerals': 5, 'credits': 10, 'result': 'ammo', 'value': 30},
    'sensor_drone': {'name': 'Sensor Drone', 'minerals': 50, 'credits': 100, 'result': 'scan', 'value': 10},
    'weapon_parts': {'name': 'Weapon Parts', 'minerals': 40, 'credits': 80, 'result': 'upgrade', 'value': 1},
    'nuclear_cell': {'name': 'Nuclear Cell', 'minerals': 100, 'credits': 200, 'result': 'damage', 'value': 15},
    'companion_chip': {'name': 'Companion Chip', 'minerals': 80, 'credits': 150, 'result': 'companion', 'value': 1},
    'warp_core': {'name': 'Warp Core', 'minerals': 200, 'credits': 500, 'result': 'warp', 'value': 1},
}

class CraftingStation:
    def __init__(self, player, hud):
        self.player = player
        self.hud = hud
        self.open = False

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.hud.set_message("CRAFTING: Press 1-8 to craft, ESC to close")
        else:
            self.hud.set_message("Crafting closed.")

    def craft(self, idx):
        keys = list(RECIPES.keys())
        if idx < 0 or idx >= len(keys):
            return
        key = keys[idx]
        recipe = RECIPES[key]
        if self.player.minerals >= recipe['minerals'] and self.player.credits >= recipe['credits']:
            self.player.minerals -= recipe['minerals']
            self.player.credits -= recipe['credits']
            result = recipe['result']
            if result == 'heal':
                self.player.hp = min(self.player.max_hp, self.player.hp + recipe['value'])
            elif result == 'max_hp':
                self.player.max_hp += recipe['value']
            elif result == 'ammo':
                pass  # Handled by weapon system
            elif result == 'scan':
                pass  # Auto-scan nearby
            elif result == 'upgrade':
                self.player.weapon_damage += 5
            elif result == 'damage':
                self.player.weapon_damage += recipe['value']
            elif result == 'companion':
                pass  # Summon random companion
            self.hud.set_message(f"Crafted {recipe['name']}!")
        else:
            self.hud.set_message(f"Need {recipe['minerals']} minerals and {recipe['credits']} CR!")

    def get_menu(self):
        lines = ["=== CRAFTING ==="]
        for i, (key, r) in enumerate(RECIPES.items()):
            lines.append(f"{i+1}. {r['name']} — {r['minerals']} minerals, {r['credits']} CR")
        return "\n".join(lines)
