"""Weapon system with multiple guns, ammo, and upgrades."""
from ursina import *
import math

WEAPON_DB = {
    'pistol': {
        'name': 'Plasma Pistol',
        'damage': 12,
        'fire_rate': 0.4,
        'range': 40,
        'ammo_max': 24,
        'spread': 0,
        'color': color.cyan,
        'auto': False,
        'projectile_speed': 30,
    },
    'rifle': {
        'name': 'Laser Rifle',
        'damage': 18,
        'fire_rate': 0.15,
        'range': 60,
        'ammo_max': 45,
        'spread': 0.02,
        'color': color.green,
        'auto': True,
        'projectile_speed': 50,
    },
    'shotgun': {
        'name': 'Nova Shotgun',
        'damage': 8,
        'fire_rate': 0.8,
        'range': 20,
        'ammo_max': 12,
        'spread': 0.15,
        'pellets': 6,
        'color': color.orange,
        'auto': False,
        'projectile_speed': 25,
    },
    'sniper': {
        'name': 'Void Sniper',
        'damage': 80,
        'fire_rate': 1.5,
        'range': 120,
        'ammo_max': 8,
        'spread': 0,
        'color': color.violet,
        'auto': False,
        'projectile_speed': 80,
    },
    'rocket': {
        'name': 'RPG-7X',
        'damage': 60,
        'fire_rate': 1.2,
        'range': 50,
        'ammo_max': 5,
        'spread': 0.05,
        'color': color.red,
        'auto': False,
        'explosive': True,
        'blast_radius': 8,
        'projectile_speed': 20,
    },
    'minigun': {
        'name': 'Gauss Minigun',
        'damage': 6,
        'fire_rate': 0.05,
        'range': 35,
        'ammo_max': 150,
        'spread': 0.08,
        'color': color.yellow,
        'auto': True,
        'projectile_speed': 40,
    },
}

class WeaponSystem:
    def __init__(self, player):
        self.player = player
        self.weapons = {k: {'unlocked': k == 'pistol', 'ammo': v['ammo_max'], 'level': 1} for k, v in WEAPON_DB.items()}
        self.current = 'pistol'
        self.cooldown = 0
        self.recoil = 0

    def get_current(self):
        return WEAPON_DB[self.current]

    def get_current_state(self):
        return self.weapons[self.current]

    def switch(self, key):
        mapping = {'1': 'pistol', '2': 'rifle', '3': 'shotgun', '4': 'sniper', '5': 'rocket', '6': 'minigun'}
        w = mapping.get(key)
        if w and self.weapons[w]['unlocked']:
            self.current = w
            return f"Switched to {WEAPON_DB[w]['name']}"
        return None

    def can_fire(self):
        return self.cooldown <= 0 and self.weapons[self.current]['ammo'] > 0

    def fire(self, origin, direction):
        if not self.can_fire():
            return []
        spec = self.get_current()
        state = self.get_current_state()
        self.cooldown = spec['fire_rate']
        self.weapons[self.current]['ammo'] -= 1
        self.recoil = min(0.3, self.recoil + 0.05)

        projectiles = []
        pellets = spec.get('pellets', 1)
        for _ in range(pellets):
            spread = spec['spread']
            if spread > 0:
                dx = random.uniform(-spread, spread)
                dy = random.uniform(-spread, spread)
                dz = random.uniform(-spread, spread)
                dir = (direction + Vec3(dx, dy, dz)).normalized()
            else:
                dir = direction
            projectiles.append({
                'origin': origin,
                'direction': dir,
                'damage': spec['damage'] * state['level'],
                'speed': spec['projectile_speed'],
                'color': spec['color'],
                'explosive': spec.get('explosive', False),
                'blast_radius': spec.get('blast_radius', 0),
                'range': spec['range'],
            })
        return projectiles

    def reload(self):
        spec = self.get_current()
        self.weapons[self.current]['ammo'] = spec['ammo_max']
        return f"Reloaded {spec['name']}"

    def unlock(self, key):
        if key in self.weapons:
            self.weapons[key]['unlocked'] = True
            self.weapons[key]['ammo'] = WEAPON_DB[key]['ammo_max']

    def upgrade(self, key):
        if key in self.weapons and self.weapons[key]['unlocked']:
            self.weapons[key]['level'] += 1
            return f"Upgraded {WEAPON_DB[key]['name']} to Mk.{self.weapons[key]['level']}"
        return None

    def add_ammo(self, key, amount):
        if key in self.weapons:
            spec = WEAPON_DB[key]
            self.weapons[key]['ammo'] = min(spec['ammo_max'], self.weapons[key]['ammo'] + amount)

    def update(self, dt):
        self.cooldown -= dt
        self.recoil = max(0, self.recoil - dt * 2)

    def get_hud_text(self):
        spec = self.get_current()
        state = self.get_current_state()
        return f"{spec['name']}  |  Ammo: {state['ammo']}/{spec['ammo_max']}  |  Lv.{state['level']}"
