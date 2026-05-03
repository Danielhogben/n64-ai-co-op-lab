
"""Random world event system.

Events:
  meteor_shower  — falling rocks from sky, damage player on hit
  enemy_raid     — wave of enemies spawns near player
  trader_caravan — temporary travelling shop with unique inventory
  anomaly        — mysterious floating object; reward on interact
"""
import random
from ursina import *
from ursina import distance

class RandomEventSystem:
    def __init__(self, player, enemy_manager, audio_manager=None):
        self.player = player
        self.enemy_mgr = enemy_manager
        self.audio = audio_manager
        self.active_events = []      # list of event dicts
        self.spawn_timer = 0
        self.spawn_interval = 120   # seconds between possible event attempts
        self.active_entities = []   # spawned Ursina entities for cleanup

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._try_spawn_random_event()

        # Update per-event logic
        for ev in self.active_events[:]:
            ev['remaining'] -= dt
            if ev['remaining'] <= 0:
                self._despawn_event(ev)

    def _try_spawn_random_event(self):
        # Don't spawn if player is in a dungeon (we'll check a flag later)
        weights = {'meteor_shower':0.25, 'enemy_raid':0.30, 'trader_caravan':0.20, 'anomaly':0.25}
        ev_type = random.choices(list(weights.keys()), weights=list(weights.values()))[0]

        # Don't spawn same event too frequently if player just experienced it
        recent = [e for e in self.active_events if e['type']==ev_type]
        if recent:
            return  # one of this type already active

        # Pick a location offset from player to avoid spawning on top
        offset = Vec3(random.uniform(-60,60), 0, random.uniform(-60,60))
        pos = self.player.position + offset
        pos.y = 5

        # Build event record
        event = {
            'id': f"{ev_type}_{int(random.random()*10000)}",
            'type': ev_type,
            'position': pos,
            'remaining': random.uniform(20, 40),  # seconds
            'max_remaining': 0,
        }
        self.active_events.append(event)
        self._spawn_event_entities(event)
        if event['type'] not in self.player.discovered_events:
            self.player.discovered_events.add(event['type'])

    def _spawn_event_entities(self, event):
        et = event['type']
        pos = event['position']
        if et == 'meteor_shower':
            # Spawn 8-12 falling fireball Entities that arc from high y to ground
            event['meteors'] = []
            for _ in range(random.randint(8,12)):
                start_y = random.uniform(60,100)
                m = Entity(model='sphere', color=color.rgb(255,120,0), scale=random.uniform(0.4,0.8),
                           position=Vec3(pos.x+random.uniform(-30,30), start_y, pos.z+random.uniform(-30,30)),
                           collider='box')
                m.impacted = False
                m.damage = random.randint(10,30)
                m.start_pos = Vec3(m.position)
                m.target_ground = m.start_pos + Vec3(0,-start_y-10,0)
                event['meteors'].append(m)
                self.active_entities.append(m)
            # HUD message
            if hasattr(self.player, 'hud') and self.player.hud:
                self.player.hud.set_message("Meteor shower incoming! Evade!", 3)

        elif et == 'enemy_raid':
            # Spawn a larger enemy group
            self.enemy_mgr.spawn_enemies(pos, danger='high', count=random.randint(6,10))
            if self.audio:
                self.audio.play('anomaly')  # placeholder alert
            # Place a marker entity
            marker = Entity(model='ring', color=color.red, position=pos, scale=2, billboard=True)
            marker.animate_scale(3, duration=1, loop=True)
            event['_marker'] = marker
            self.active_entities.append(marker)
            if self.player.hud:
                self.player.hud.set_message("Enemy raid detected! Prepare to fight!", 3)

        elif et == 'trader_caravan':
            # Spawn a temporary shop entity
            caravan = Entity(model='cube', color=color.rgb(200,180,100), position=pos, scale=(2,2,4), collider='box')
            caravan.shop_inventory = {
                'rare_tech':    {'buy': 500,  'sell': 200, 'stock':2, 'desc':'Powerful weapon mod'},
                'shield_cell':  {'buy': 120,  'sell': 50,  'stock':5, 'desc':'Restores 50 shield'},
                'energy_core':  {'buy': 800,  'sell': 300, 'stock':1, 'desc':'+50 max shield'},
                'star_chart':   {'buy': 1000, 'sell': 0,   'stock':1, 'desc':'Reveals ROM sector'},
            }
            caravan.interact_cooldown = 0
            event['caravan'] = caravan
            self.active_entities.append(caravan)
            if self.player.hud:
                self.player.hud.set_message("Trader caravan arrived! Press E to trade.", 4)

        elif et == 'anomaly':
            # Floating ripple effect
            core = Entity(model='sphere', color=color.rgba(180,0,255,200), position=pos, scale=1.5,
                          collider='box')
            core.animate_scale_y(2.2, duration=2, loop=True, curve=curve.sin)
            core.value = random.randint(80,200)  # mineral/xp value
            core.reward_type = random.choice(['credits','minerals','xp'])
            event['anomaly'] = core
            self.active_entities.append(core)
            if self.player.hud:
                self.player.hud.set_message("Space anomaly detected! Approach to scan.", 3)

    def _despawn_event(self, event):
        # Cleanup
        for ent in self.active_entities[:]:
            if any(ent is v for v in [event.get('meteors',[]), event.get('anomaly'), event.get('caravan'), event.get('_marker')]):
                self.active_entities.remove(ent)
                destroy(ent)
        # Remove references
        for key in ['meteors','anomaly','caravan','_marker']:
            if key in event:
                del event[key]
        if event in self.active_events:
            self.active_events.remove(event)

    def get_meteor_collisions(self):
        hits = []
        for ev in self.active_events:
            if ev['type'] == 'meteor_shower':
                for m in ev.get('meteors', []):
                    if not m.impacted and distance(m.position, self.player.position) < 1.2:
                        m.impacted = True
                        hits.append(m)
        return hits
