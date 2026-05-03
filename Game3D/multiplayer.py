import random, math
from ursina import *
from ursina import distance

class Player2(Entity):
    def __init__(self):
        super().__init__(model='cube', color=color.rgb(255,200,0), scale=(0.8,1.8,0.8),
                         position=(2,5,0), collider='box')
        self.speed = 6
        self.run_speed = 10
        self.y_velocity = 0
        self.grounded = False
        self.shoot_cooldown = 0
        self.weapon_damage = 15
        self.hp = 100
        self.max_hp = 100
        self.credits = 1000
        self.xp = 0
        self.level = 1
        self.minerals = 0
        self.camera_pivot = Entity(parent=self, position=(0,1.6,0))
        self.camera = Camera(parent=self.camera_pivot)
        self.camera.fov = 90
        self.camera.viewport = (0.5, 0, 0.5, 1)
        self.key_map = {
            'forward': 'up arrow',
            'backward': 'down arrow',
            'left': 'left arrow',
            'right': 'right arrow',
            'run': 'right shift',
            'jump': 'right control',
            'shoot': 'num0',
        }
        self.gamepad_available = False

    def update(self):
        dt = time.dt
        move = Vec3(0,0,0)
        if held_keys[self.key_map['forward']]:
            move += self.camera_pivot.forward
        if held_keys[self.key_map['backward']]:
            move -= self.camera_pivot.forward
        if held_keys[self.key_map['left']]:
            move -= self.camera_pivot.right
        if held_keys[self.key_map['right']]:
            move += self.camera_pivot.right
        move.y = 0
        if move.length() > 0:
            move = move.normalized()
            speed = self.run_speed if held_keys[self.key_map['run']] else self.speed
            self.position += move * speed * dt
            angle = math.degrees(math.atan2(move.x, move.z))
            self.rotation_y = lerp(self.rotation_y, angle, 8*dt)
        ground_y = 0.5
        if self.y <= ground_y + 1:
            self.y = ground_y + 1
            self.grounded = True
            self.y_velocity = 0
        else:
            self.grounded = False
            self.y_velocity -= 20 * dt
            self.y += self.y_velocity * dt
        if held_keys[self.key_map['jump']] and self.grounded:
            self.y_velocity = 8
            self.grounded = False
        self.shoot_cooldown -= dt
        if held_keys[self.key_map['shoot']] and self.shoot_cooldown <= 0:
            self._shoot()
            self.shoot_cooldown = 0.4

    def _shoot(self):
        forward = self.camera_pivot.forward
        hit_info = raycast(self.position + Vec3(0,1.5,0), forward, distance=50, ignore=[self])
        if hit_info.hit and hasattr(hit_info.entity, 'take_damage'):
            hit_info.entity.take_damage(self.weapon_damage)
        beam = Entity(model='cube', scale=(0.05,0.05,40), color=color.yellow)
        beam.position = self.position + Vec3(0,1.5,0)
        beam.rotation = self.camera_pivot.rotation
        destroy(beam, delay=0.1)

class SplitScreenManager:
    def __init__(self, player_main):
        self.p1 = player_main
        self.p2 = Player2()
        self.active = True
        # P1 viewport: left half (0,0,0.5,1); P2 viewport already set in Player2
        camera.viewport = (0, 0, 0.5, 1)
        camera.enabled = self.active
        self.p2.camera.enabled = self.active
    def update(self, dt):
        self.p2.update()
    def toggle(self):
        self.active = not self.active
        camera.enabled = self.active
        self.p2.camera.enabled = self.active
