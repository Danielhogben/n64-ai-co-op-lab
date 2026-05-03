"""Boss arenas with unique boss fights."""
import random, math, time as py_time
from ursina import *

class Boss(Entity):
    def __init__(self, pos, btype='Eldoria'):
        scales = {'Eldoria': 3, 'Nebula Tyrant': 4, 'Nexus Prime': 5}
        colors = {'Eldoria': color.violet, 'Nebula Tyrant': color.red, 'Nexus Prime': color.gold}
        super().__init__(
            model='cube',
            color=colors.get(btype, color.white),
            position=pos,
            scale=scales.get(btype, 3),
            collider='box'
        )
        self.btype = btype
        self.hp = {'Eldoria': 500, 'Nebula Tyrant': 800, 'Nexus Prime': 1500}.get(btype, 500)
        self.max_hp = self.hp
        self.phase = 1
        self.attack_timer = 0
        self.pattern_timer = 0
        self.minions = []
        self.projectiles = []
        self.spawn_time = py_time.time()

    def update(self, player, dt, hud):
        dist = distance(self.position, player.position)
        self.attack_timer -= dt
        self.pattern_timer -= dt

        # Phase transitions based on HP
        hp_pct = self.hp / self.max_hp
        if hp_pct < 0.3:
            self.phase = 3
            self.color = color.red
        elif hp_pct < 0.6:
            self.phase = 2
            self.color = color.orange

        # Look at player
        self.look_at(player.position)

        # Attack patterns
        if self.attack_timer <= 0:
            self.attack_timer = max(0.5, 2.5 - self.phase * 0.5)
            if self.btype == 'Eldoria':
                self.eldoria_attack(player, hud)
            elif self.btype == 'Nebula Tyrant':
                self.tyrant_attack(player, hud)
            elif self.btype == 'Nexus Prime':
                self.prime_attack(player, hud)

        # Minion management
        for m in self.minions[:]:
            if not m or m.hp <= 0:
                self.minions.remove(m)

        # Projectiles
        for p in self.projectiles[:]:
            if p['life'] <= 0:
                self.projectiles.remove(p)
                continue
            p['entity'].position += p['direction'] * p['speed'] * dt
            p['life'] -= dt
            if distance(p['entity'].position, player.position) < 1.5:
                player.hp -= p['damage']
                hud.set_message(f"Boss hit you! -{p['damage']} HP")
                destroy(p['entity'])
                self.projectiles.remove(p)

    def eldoria_attack(self, player, hud):
        # Pattern: Laser barrage (phase 1), Summon minions (phase 2), Charge (phase 3)
        if self.phase == 1:
            # Spread shot
            for angle in [-30, 0, 30]:
                rad = math.radians(self.rotation_y + angle)
                dir = Vec3(math.sin(rad), 0, math.cos(rad))
                self.spawn_projectile(dir, 15, 10)
            hud.set_message("Eldoria: Laser Barrage!")
        elif self.phase == 2:
            # Summon minions
            for _ in range(2):
                m = Entity(model='cube', color=color.dark_gray, scale=0.8, position=self.position + Vec3(random.uniform(-5, 5), 0, random.uniform(-5, 5)), collider='box')
                m.hp = 30
                self.minions.append(m)
            hud.set_message("Eldoria: Summoning drones!")
        else:
            # Charge at player
            dir = (player.position - self.position).normalized()
            self.position += dir * 15 * time.dt
            if distance(self.position, player.position) < 3:
                player.hp -= 20
                hud.set_message("Eldoria CHARGED! -20 HP")

    def tyrant_attack(self, player, hud):
        # Pattern: Fire nova, Ground slam, Meteor call
        if self.phase == 1:
            # Nova burst
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                dir = Vec3(math.sin(rad), 0, math.cos(rad))
                self.spawn_projectile(dir, 10, 8)
            hud.set_message("Tyrant: Fire Nova!")
        elif self.phase == 2:
            # Ground slam - shockwave
            shock = Entity(model='sphere', color=color.red, scale=0.5, position=self.position)
            shock.animate_scale(8, duration=1)
            destroy(shock, delay=1)
            if distance(self.position, player.position) < 8:
                player.hp -= 15
                hud.set_message("Tyrant SLAM! -15 HP")
        else:
            # Meteor rain
            for _ in range(3):
                met = Entity(model='sphere', color=color.orange, scale=0.8, position=player.position + Vec3(random.uniform(-10, 10), 20, random.uniform(-10, 10)))
                met.animate_position(met.position - Vec3(0, 25, 0), duration=1.2)
                destroy(met, delay=1.2)
            hud.set_message("Tyrant: Meteor Rain!")

    def prime_attack(self, player, hud):
        # Pattern: Time warp (slows player), Black hole, Death ray
        if self.phase == 1:
            # Multi-directional shot
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                dir = Vec3(math.sin(rad), 0, math.cos(rad))
                self.spawn_projectile(dir, 20, 12)
            hud.set_message("Nexus Prime: Death Array!")
        elif self.phase == 2:
            # Black hole pull
            pull = Entity(model='sphere', color=color.black, scale=2, position=self.position)
            pull.animate_scale(6, duration=2)
            destroy(pull, delay=2)
            if distance(self.position, player.position) < 10:
                dir = (self.position - player.position).normalized()
                player.position += dir * 5 * time.dt
                player.hp -= 2
            hud.set_message("Nexus Prime: Singularity!")
        else:
            # Death ray - sustained beam
            beam = Entity(model='cube', color=color.gold, scale=(0.5, 0.5, 30))
            beam.position = self.position + self.forward * 15
            beam.rotation_y = self.rotation_y
            destroy(beam, delay=2)
            if distance(self.position, player.position) < 30:
                player.hp -= 30 * time.dt
                hud.set_message("Nexus Prime: DEATH RAY!")

    def spawn_projectile(self, direction, speed, damage):
        p = Entity(model='sphere', color=self.color, scale=0.4, position=self.position + Vec3(0, 1, 0))
        self.projectiles.append({
            'entity': p,
            'direction': direction,
            'speed': speed,
            'damage': damage,
            'life': 3,
        })

    def take_damage(self, amount):
        self.hp -= amount
        self.blink(color.white, duration=0.1)
        if self.hp <= 0:
            self.die()

    def die(self):
        for _ in range(20):
            p = Entity(model='sphere', color=self.color, scale=0.5, position=self.position)
            p.animate_position(self.position + Vec3(random.uniform(-10, 10), random.uniform(0, 10), random.uniform(-10, 10)), duration=1)
            destroy(p, delay=1)
        for p in self.projectiles:
            destroy(p['entity'])
        for m in self.minions:
            destroy(m)
        destroy(self)


class BossArenaManager:
    def __init__(self):
        self.active_boss = None
        self.arenas = []

    @property
    def active(self):
        return self.active_boss is not None

    def spawn_boss(self, pos, btype):
        if self.active_boss:
            return None
        self.active_boss = Boss(pos, btype)
        return self.active_boss

    def update(self, player, dt, hud):
        if self.active_boss and self.active_boss.hp > 0:
            self.active_boss.update(player, dt, hud)
        elif self.active_boss and self.active_boss.hp <= 0:
            self.active_boss = None
