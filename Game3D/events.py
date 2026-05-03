"""Random world events that spawn dynamically."""
import random, math
from ursina import *

EVENT_TYPES = ['meteor_shower', 'enemy_raid', 'trader_caravan', 'anomaly', 'solar_flare']

class WorldEvent:
    def __init__(self, etype, pos):
        self.etype = etype
        self.pos = pos
        self.timer = 0
        self.duration = random.randint(30, 90)
        self.active = True
        self.entities = []
        self.spawn_visuals()

    def spawn_visuals(self):
        if self.etype == 'meteor_shower':
            self.entities.append(Text(text="METEOR SHOWER INCOMING!", position=(0, 0.3), origin=(0,0), scale=2, color=color.red))
        elif self.etype == 'enemy_raid':
            self.entities.append(Text(text="ENEMY RAID DETECTED!", position=(0, 0.3), origin=(0,0), scale=2, color=color.orange))
        elif self.etype == 'trader_caravan':
            self.entities.append(Text(text="TRADER CARAVAN NEARBY!", position=(0, 0.3), origin=(0,0), scale=2, color=color.green))
        elif self.etype == 'anomaly':
            self.entities.append(Text(text="SPATIAL ANOMALY DETECTED!", position=(0, 0.3), origin=(0,0), scale=2, color=color.violet))
        elif self.etype == 'solar_flare':
            self.entities.append(Text(text="SOLAR FLARE! SHIELDS DOWN!", position=(0, 0.3), origin=(0,0), scale=2, color=color.yellow))

    def update(self, dt, player, enemy_mgr, hud):
        self.timer += dt
        if self.timer > 5:
            for e in self.entities:
                if isinstance(e, Text):
                    destroy(e)
            self.entities = []

        if self.etype == 'meteor_shower':
            if random.random() < 0.1:
                m = Entity(model='sphere', color=color.red, scale=0.5, position=player.position + Vec3(random.uniform(-20, 20), 30, random.uniform(-20, 20)))
                m.animate_position(m.position - Vec3(0, 40, 0), duration=1.5, curve=curve.linear)
                destroy(m, delay=1.5)
                if random.random() < 0.3:
                    player.hp -= 5
                    hud.set_message("Meteor hit! -5 HP")

        elif self.etype == 'enemy_raid':
            if random.random() < 0.05 and self.timer < self.duration:
                enemy_mgr.spawn_enemies(player.position, 'high', 2)

        elif self.etype == 'trader_caravan':
            if distance(player.position, self.pos) < 10 and random.random() < 0.02:
                player.credits += random.randint(50, 150)
                hud.set_message("Trader gave you credits!")

        elif self.etype == 'anomaly':
            if distance(player.position, self.pos) < 15:
                player.xp += 1
                if random.random() < 0.01:
                    player.credits += 100
                    hud.set_message("Anomaly anomaly! Found 100 CR!")

        elif self.etype == 'solar_flare':
            if hasattr(player, 'shield_strength'):
                player.shield_strength = max(0, player.shield_strength - 10 * dt)

        if self.timer >= self.duration:
            self.active = False
            for e in self.entities:
                destroy(e)


class EventManager:
    def __init__(self):
        self.events = []
        self.spawn_timer = 0

    def update(self, dt, player, enemy_mgr, hud):
        self.spawn_timer += dt
        if self.spawn_timer > 45:
            self.spawn_timer = 0
            etype = random.choice(EVENT_TYPES)
            pos = player.position + Vec3(random.uniform(-50, 50), 0, random.uniform(-50, 50))
            evt = WorldEvent(etype, pos)
            self.events.append(evt)
            hud.set_message(f"EVENT: {etype.replace('_', ' ').title()}!")

        for evt in self.events[:]:
            evt.update(dt, player, enemy_mgr, hud)
            if not evt.active:
                self.events.remove(evt)
