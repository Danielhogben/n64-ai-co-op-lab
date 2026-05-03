"""Enemy AI and combat system with day/night behavior."""
import random, math
from ursina import *
from universe import Universe

uni = Universe()


class Enemy(Entity):
    def __init__(self, pos, etype='drone'):
        colors = {
            'drone': color.rgb(200, 60, 60),
            'sentinel': color.rgb(150, 0, 200),
            'marauder': color.rgb(200, 100, 0),
            'boss': color.rgb(80, 0, 0),
        }
        scales = {'drone': 1, 'sentinel': 1.3, 'marauder': 1.1, 'boss': 2.5}
        hps = {'drone': 30, 'sentinel': 60, 'marauder': 45, 'boss': 300}

        super().__init__(
            model='cube',
            color=colors.get(etype, color.red),
            position=pos,
            scale=scales.get(etype, 1),
            collider='box'
        )
        self.etype = etype
        self.hp = hps.get(etype, 30)
        self.max_hp = self.hp
        self.speed = random.uniform(1.5, 3.5)
        self.state = 'patrol'
        self.patrol_center = Vec3(pos)
        self.patrol_target = self.random_patrol_point()
        self.attack_cooldown = 0
        self.detection_range = 25 if etype != 'boss' else 40
        self.attack_range = 15
        self.damage = {'drone': 5, 'sentinel': 10, 'marauder': 8, 'boss': 25}.get(etype, 5)
        self.is_night = False  # set by manager each frame
        self.sleep_timer = 0

        # HP bar
        self.hp_bar = Entity(parent=self, model='cube', scale=(1.2, 0.15, 0.1), position=(0, 1.2, 0), color=color.green)

    def random_patrol_point(self):
        return self.patrol_center + Vec3(random.uniform(-15, 15), 0, random.uniform(-15, 15))

    def update(self, player_pos, dt, is_night=False):
        self.is_night = is_night

        # Night behavior: enemies sleep (inactive) after 20:00–04:00
        if self.is_night:
            if not hasattr(self, '_was_active'):
                self._was_active = True
            # Try to return to spawn and sleep
            d_home = distance(self.position, self.patrol_center)
            if d_home > 2:
                # Walk slowly back to spawn
                self.move_toward(self.patrol_center, self.speed * 0.3)
                self._was_active = True
            else:
                # Sleeping: don't move, don't chase
                self._was_active = False
            # Skip chase/logic
            return
        else:
            self._was_active = True  # enemy is active during day

        dist = distance(self.position, player_pos)

        # State machine
        if dist < self.detection_range:
            self.state = 'chase'
        elif self.state == 'chase' and dist > self.detection_range * 1.5:
            self.state = 'patrol'
            self.patrol_target = self.random_patrol_point()

        if self.state == 'patrol':
            self.move_toward(self.patrol_target, self.speed * 0.5)
            if distance(self.position, self.patrol_target) < 2:
                self.patrol_target = self.random_patrol_point()
        elif self.state == 'chase':
            self.move_toward(player_pos, self.speed)
            self.look_at(player_pos)
            if dist < self.attack_range and self.attack_cooldown <= 0:
                self.attack()
                self.attack_cooldown = 1.5

        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        # Update HP bar
        if self.hp_bar:
            self.hp_bar.scale_x = 1.2 * (self.hp / self.max_hp)
            self.hp_bar.color = color.green if self.hp / self.max_hp > 0.5 else color.yellow if self.hp / self.max_hp > 0.25 else color.red

    def move_toward(self, target, speed):
        direction = (target - self.position).normalized()
        direction.y = 0
        self.position += direction * speed * time.dt
        if direction.length() > 0.01:
            self.rotation_y = math.degrees(math.atan2(direction.x, direction.z))

    def attack(self):
        # Spawn projectile
        proj = Entity(
            model='sphere',
            color=color.red,
            scale=0.3,
            position=self.position + Vec3(0, 0.5, 0)
        )
        proj.animate_position(self.position + (self.forward * 20), duration=0.8, curve=curve.linear)
        destroy(proj, delay=0.8)

    def take_damage(self, amount):
        self.hp -= amount
        self.blink(color.white, duration=0.1)
        if self.hp <= 0:
            self.die()

    def die(self):
        # Explosion particles
        for _ in range(8):
            p = Entity(model='sphere', color=self.color, scale=0.2, position=self.position)
            p.animate_position(self.position + Vec3(random.uniform(-3, 3), random.uniform(0, 3), random.uniform(-3, 3)), duration=0.5)
            destroy(p, delay=0.5)
        destroy(self.hp_bar)
        destroy(self)


class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.max_enemies = 15
        self._day_time = True  # default

    def spawn_enemies(self, center, danger='medium', count=5):
        types = ['drone'] * 3 + ['sentinel'] * 2 + ['marauder'] * 2
        if danger == 'high':
            types = ['drone', 'sentinel', 'marauder']
        elif danger == 'extreme':
            types = ['sentinel', 'marauder', 'boss']

        for _ in range(count):
            if len(self.enemies) >= self.max_enemies:
                break
            etype = random.choice(types)
            pos = center + Vec3(random.uniform(-30, 30), 5, random.uniform(-30, 30))
            e = Enemy(pos, etype)
            self.enemies.append(e)

    def update(self, player_pos, dt, is_night=False):
        self._day_time = not is_night
        for e in self.enemies[:]:
            if not e or e.hp <= 0:
                self.enemies.remove(e)
                continue
            e.update(player_pos, dt, is_night=is_night)

    def clear_far(self, player_pos, max_dist=100):
        for e in self.enemies[:]:
            if distance(e.position, player_pos) > max_dist:
                destroy(e.hp_bar)
                destroy(e)
                self.enemies.remove(e)
