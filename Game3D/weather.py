"""Weather system with rain, fog, sandstorm, snow."""
import random, math
from ursina import *

class WeatherSystem(Entity):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.current = 'clear'
        self.intensity = 0
        self.timer = 0
        self.change_timer = 0
        self.particles = []
        self.fog_entity = None
        self.wind_dir = Vec3(1, 0, 0)

    def set_weather(self, wtype, duration=60):
        self.current = wtype
        self.timer = duration
        self.intensity = 0
        if self.fog_entity:
            destroy(self.fog_entity)
            self.fog_entity = None
        if wtype == 'fog':
            self.fog_entity = Entity(model='sphere', color=color.rgba(200, 200, 220, 100), scale=200, position=self.player.position)
        elif wtype == 'sandstorm':
            self.fog_entity = Entity(model='sphere', color=color.rgba(180, 150, 100, 120), scale=200, position=self.player.position)

    def update(self, dt):
        self.change_timer += dt
        if self.change_timer > 90:
            self.change_timer = 0
            choices = ['clear', 'rain', 'fog', 'sandstorm', 'snow']
            weights = [40, 25, 15, 10, 10]
            new_weather = random.choices(choices, weights=weights)[0]
            if new_weather != self.current:
                self.set_weather(new_weather)

        self.timer -= dt
        if self.timer <= 0 and self.current != 'clear':
            self.set_weather('clear', 9999)

        self.intensity = min(1, self.intensity + dt * 0.5)

        # Update fog position
        if self.fog_entity:
            self.fog_entity.position = self.player.position

        # Particle effects
        if self.current in ('rain', 'snow', 'sandstorm'):
            spawn_rate = {'rain': 0.02, 'snow': 0.05, 'sandstorm': 0.03}.get(self.current, 0.02)
            if random.random() < spawn_rate * self.intensity:
                offset = Vec3(random.uniform(-20, 20), 20, random.uniform(-20, 20))
                pos = self.player.position + offset
                if self.current == 'rain':
                    p = Entity(model='cube', color=color.rgba(150, 150, 255, 150), scale=(0.05, 0.5, 0.05), position=pos)
                    p.animate_position(pos - Vec3(0, 25, 0), duration=0.8)
                elif self.current == 'snow':
                    p = Entity(model='sphere', color=color.white, scale=0.1, position=pos)
                    p.animate_position(pos - Vec3(random.uniform(-2, 2), 20, random.uniform(-2, 2)), duration=3)
                elif self.current == 'sandstorm':
                    p = Entity(model='sphere', color=color.rgba(180, 150, 100, 100), scale=0.15, position=pos)
                    p.animate_position(pos + Vec3(20, random.uniform(-5, 5), random.uniform(-5, 5)), duration=2)
                destroy(p, delay=2)

    def get_name(self):
        return self.current.replace('_', ' ').title()
