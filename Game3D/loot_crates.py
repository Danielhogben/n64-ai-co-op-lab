import random
from ursina import *

class LootCrate(Entity):
    def __init__(self, position):
        super().__init__(model='cube', color=color.rgb(200,150,100), scale=(1,0.8,0.8),
                         position=position, collider='box')
        self.opened = False
    def update(self):
        if not self.opened:
            self.rotation_y += 15 * time.dt
            self.y = lerp(self.y, 1.5 + math.sin(time.time()*2)*0.1, time.dt*5)
    def interact(self, player, audio=None):
        if self.opened:
            return "Already looted."
        self.opened = True
        self.color = color.gray
        self.scale = (0.9,0.1,0.9)
        loot = random.choice([
            {'type':'credits','amount':random.randint(50,200)},
            {'type':'minerals','amount':random.randint(30,120)},
            {'type':'weapon_part','amount':1},
            {'type':'shield_boost','amount':25},
        ])
        if loot['type']=='credits': player.credits += loot['amount']
        elif loot['type']=='minerals': player.minerals += loot['amount']
        elif loot['type']=='weapon_part': player.weapon_damage += 3
        elif loot['type']=='shield_boost':
            player.shield_strength = min(getattr(player,'max_shield',100), player.shield_strength + loot['amount'])
        if audio: audio.play('crate_open')
        return f"Loot: {loot['amount']} {loot['type']}"

class LootCrateManager:
    def __init__(self, player, audio=None):
        self.player = player
        self.audio = audio
        self.crates = []
        self.spawn_timer = 0
        self.spawn_interval = 45
        self.max_crates = 8

    def update(self):
        self.spawn_timer += time.dt
        if self.spawn_timer >= self.spawn_interval and len(self.crates) < self.max_crates:
            self.spawn_timer = 0
            self.spawn_crate()
        for c in self.crates[:]:
            if c.opened:
                self.crates.remove(c)
                destroy(c)

    def spawn_crate(self):
        offset = Vec3(random.uniform(-50,50), 0, random.uniform(-50,50))
        pos = self.player.position + offset
        pos.y = 2
        crate = LootCrate(position=pos)
        self.crates.append(crate)

    def get_nearby_crate(self, max_dist=4):
        for crate in self.crates:
            if not crate.opened and distance(crate.position, self.player.position) < max_dist:
                return crate
        return None
