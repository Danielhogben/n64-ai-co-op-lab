
"""Weather system: rain, fog, lightning storms.

Integrates with player.exposure and player.shield_strength.
"""
import random
from ursina import *
from ursina import distance, lerp

class WeatherSystem(Entity):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.rain_particles = []
        self.weather = 'clear'   # 'clear' | 'rain' | 'storm' | 'fog'
        self.fog_density = 0.0
        self.storm_active = False
        self.lightning_timer = 0
        self.lightning_cooldown = random.uniform(5, 15)
        self.rain_intensity = 0.0
        scene.fog_density = 0.0
        scene.fog_color = color.white

    def set_weather(self, weather_type):
        self.weather = weather_type
        if weather_type == 'clear':
            self.fog_density  = 0.0
            self.rain_intensity = 0.0
            self.storm_active = False
        elif weather_type == 'rain':
            self.fog_density  = 0.0
            self.rain_intensity = 0.5
            self.storm_active = False
        elif weather_type == 'storm':
            self.fog_density  = 0.0
            self.rain_intensity = 1.0
            self.storm_active = True
            self.lightning_cooldown = random.uniform(2, 5)
        elif weather_type == 'fog':
            self.fog_density  = 0.6
            self.rain_intensity = 0.0
            self.storm_active = False
        # Smooth visual transitions
        scene.fog_density = self.fog_density

    def update(self):
        dt = time.dt

        # Update player exposure (affects HUD overlay)
        target_exp = 0.0
        if self.weather in ('rain', 'storm'):
            target_exp = 0.3 * self.rain_intensity
        if self.weather == 'fog':
            target_exp = self.fog_density
        self.player.exposure = lerp(self.player.exposure, target_exp, dt * 0.5)

        # Ensure global fog matches state
        scene.fog_density = lerp(scene.fog_density, self.fog_density, dt)
        scene.fog_color = color.rgba(180, 190, 200, 255)

        # Rain particles
        target_count = int(self.rain_intensity * 150)
        self._adjust_rain_count(target_count)
        self._update_rain_particles(dt)

        # Lightning in storms
        if self.storm_active:
            self.lightning_timer += dt
            if self.lightning_timer >= self.lightning_cooldown:
                self._trigger_lightning()
                self.lightning_timer = 0
                self.lightning_cooldown = random.uniform(1.5, 4.0)

    def _adjust_rain_count(self, target):
        while len(self.rain_particles) < target:
            p = Entity(model='quad', scale=0.05,
                       color=color.rgba(160, 200, 255, 180),
                       position=Vec3(random.uniform(-60, 60), random.uniform(40, 60), random.uniform(-60, 60)),
                       billboard=True)
            p.velocity = Vec3(0, -random.uniform(10, 18), 0)
            self.rain_particles.append(p)
        while len(self.rain_particles) > target:
            p = self.rain_particles.pop()
            destroy(p)

    def _update_rain_particles(self, dt):
        for p in self.rain_particles:
            p.y += p.velocity.y * dt
            if p.y < 0:
                p.y = random.uniform(40, 60)
                p.x, p.z = random.uniform(-60, 60), random.uniform(-60, 60)

    def _trigger_lightning(self):
        # Flash white overlay
        flash = Entity(parent=camera.ui, model='quad', scale=(2, 1), color=color.white, z=0.1)
        destroy(flash, delay=0.08)
        # Audio handled by AudioManager hook elsewhere
        # Chance to damage player shield
        if self.player and distance(self.player.position, Vec3(0,0,0)) < 80:
            dmg = random.randint(15, 50)
            self.player.shield_strength = max(0, self.player.shield_strength - dmg)

# Convenience function for random weather changes
def random_weather_transition(weather_sys, interval=60):
    """Call every 'interval' seconds to possibly change weather."""
    if random.random() < 0.3:  # 30% chance to shift
        weights = [0.4, 0.25, 0.2, 0.15]  # clear, rain, storm, fog
        choice = random.choices(['clear','rain','storm','fog'], weights=weights)[0]
        weather_sys.set_weather(choice)
