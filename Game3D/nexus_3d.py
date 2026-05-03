#!/usr/bin/env python3
"""
Project Nexus: Space Universe — 3D Third-Person Action Game
Built with Ursina Engine. Explore galaxies, build bases, fight enemies,
collect Pokemon companions, and discover all 362 ROM worlds.

Features implemented:
  - Quest system (quest giver NPCs, quest log, rewards)
  - Trading economy (shops in neutral cities)
  - Vehicle summoning (V = hoverbike, Shift+V = ship)
  - Day/night cycle (enemies sleep at night)
  - N64 Hyrule Field floor textures on terrain
  - Persistent save/load (JSON)
"""
import random, math, os, json, time as py_time
from ursina import *
from world_generator import World, QuestGiver, Shop, Vehicle
from enemy_system import EnemyManager
from universe import Universe
from sound_system import SoundManager
from weather_system import WeatherSystem
from event_system import RandomEventSystem
from dungeon_generator import Dungeon, PortalExit, Chest
from boss_arenas import BossArenaManager
from loot_system import LootManager
from multiplayer import SplitScreenManager as MultiplayerManager
from weapons import WeaponSystem
from skill_tree import SkillTree
from crafting import CraftingStation
from story_missions import StoryManager

app = Ursina(title="Project Nexus: Space Universe", borderless=False)
window.size = (1280, 720)
window.fullscreen = False

# ── ASSETS ──
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(GAME_DIR, 'save.json')
os.chdir(GAME_DIR)

# ── DATA ──
uni = Universe()
world = World()
enemy_mgr = EnemyManager()

# ── DAY / NIGHT CYCLE ──
class DayNightCycle(Entity):
    """Rotates sun, changes sky/environment colors, controls enemy sleep."""
    def __init__(self):
        super().__init__()
        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1, -1, -1))
        self.sun.color = color.rgba(255, 255, 200, 100)
        self.sky = Sky()
        self.sky.texture = 'sky_default'
        self.sky.color = color.rgba(100, 150, 255, 255)
        self.time_of_day = 0.5  # 0.0 = midnight, 0.5 = noon, 1.0 = midnight
        self.day_length = 300  # seconds per full day cycle

    def update(self):
        # Advance time
        self.time_of_day += time.dt / self.day_length
        if self.time_of_day >= 1.0:
            self.time_of_day = 0.0

        # Sun angle (0 = midnight behind, 0.25 = sunrise, 0.5 = noon, 0.75 = sunset)
        angle = self.time_of_day * math.pi * 2
        sun_x = math.sin(angle)
        sun_y = -math.cos(angle)  # negative so sun rises, sets above horizon
        self.sun.look_at(Vec3(sun_x, sun_y, -0.5))

        # Night flag: 20:00–04:00 maps to [0.83, 0.11) in 0-1 scale
        is_night = (self.time_of_day >= 0.83) or (self.time_of_day < 0.11)

        # Sky / ambient colors
        if is_night:
            ambient = color.rgba(20, 20, 60, 100)
            sky_tint = color.rgba(10, 10, 60, 255)
            sun_col = color.rgba(200, 200, 255, 60)
        else:
            # Day colors shift with hour
            t = self.time_of_day
            if 0.25 <= t < 0.75:  # full daylight
                ambient = color.rgba(100, 100, 120, 80)
                sky_tint = color.rgba(100, 150, 255, 255)
                sun_col = color.rgba(255, 250, 200, 120)
            else:  # dawn/dusk
                ambient = color.rgba(80, 60, 80, 90)
                sky_tint = color.rgba(120, 80, 120, 255)
                sun_col = color.rgba(255, 150, 100, 100)

        AmbientLight(color=ambient)
        self.sky.color = sky_tint
        self.sun.color = sun_col

        return is_night


day_night = DayNightCycle()


# ── PLAYER ──
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.rgb(0, 255, 150),
            scale=(0.8, 1.8, 0.8),
            position=(0, 5, 0),
            collider='box'
        )
        self.speed = 6
        self.run_speed = 10
        self.mouse_sensitivity = 40
        self.y_velocity = 0
        self.grounded = False
        self.shoot_cooldown = 0
        self.weapon_damage = 15
        self.angle = 0

        # Stats
        self.hp = 100
        self.max_hp = 100
        self.credits = 1000
        self.xp = 0
        self.level = 1
        self.minerals = 0
        self.mineral_bonus = 0  # from shop upgrades
        self.scan_range = 100   # ROM scan range
        self.bases = []
        self.discovered_roms = set()
        self.active_pokemon = None

        # Audio / sound preferences
        self.sound_enabled = True
        self.master_volume = 0.8

        # Weather shield stats
        self.shield_strength = 100   # absorbs lightning damage
        self.max_shield = 100
        self.exposure = 0.0  # 0-1, visibility reduction from fog/rain

        # Random event discovery tracking
        self.event_cooldowns = {}   # event_type -> timestamp when available again
        self.discovered_events = set()  # ids of seen random events

        # Loot tracking
        self.looted_crate_ids = set()

        # Quest tracking
        self.active_quests = []   # list of quest objects (references)
        self.completed_quests = []

        # Vehicle
        self.vehicle = None

    def load_save(self):
        save_path = SAVE_PATH
        if os.path.exists(save_path):
            try:
                with open(save_path) as f:
                    data = json.load(f)
                for k in ['hp', 'max_hp', 'credits', 'xp', 'level', 'minerals', 'shield_strength', 'max_shield']:
                    if k in data:
                        setattr(self, k, data[k])
                self.bases = data.get('bases', [])
                self.discovered_roms = set(data.get('discovered_roms', []))
                self.active_pokemon = data.get('active_pokemon')
                self.sound_enabled = data.get('sound_enabled', True)
                self.master_volume = data.get('master_volume', 0.8)
                self.shield_strength = data.get('shield_strength', self.shield_strength)
                self.max_shield = data.get('max_shield', self.max_shield)
                self.exposure = data.get('exposure', 0.0)
                self.discovered_events = set(data.get('discovered_events', []))
                self.looted_crate_ids = set(data.get('looted_crate_ids', []))
                self.position = Vec3(*data.get('pos', [0, 5, 0]))
            except Exception as e:
                print("Save load error:", e)

    def save(self):
        save_path = SAVE_PATH
        data = {
            'hp': self.hp, 'max_hp': self.max_hp, 'credits': self.credits,
            'xp': self.xp, 'level': self.level, 'minerals': self.minerals,
            'shield_strength': self.shield_strength, 'max_shield': self.max_shield,
            'exposure': self.exposure, 'sound_enabled': self.sound_enabled,
            'master_volume': self.master_volume,
            'bases': self.bases, 'discovered_roms': list(self.discovered_roms),
            'discovered_events': list(self.discovered_events),
            'looted_crate_ids': list(self.looted_crate_ids),
            'active_pokemon': self.active_pokemon,
            'pos': [self.x, self.y, self.z]
        }
        # Save weapon / skill / story state if managers exist
        try:
            data['weapon_unlocks'] = {k: {'unlocked': v['unlocked'], 'ammo': v['ammo'], 'level': v['level']} for k, v in weapon_sys.weapons.items()}
        except:
            pass
        try:
            data['skill_ranks'] = skill_tree.ranks
            data['skill_points'] = skill_tree.points
        except:
            pass
        try:
            data['story_chapter'] = story_mgr.current_idx
            data['visited_galaxies'] = list(story_mgr.visited_galaxies)
            data['built_galaxies'] = list(story_mgr.built_galaxies)
        except:
            pass
        with open(save_path, 'w') as f:
            json.dump(data, f)


class ThirdPersonCamera(Entity):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.distance = 8
        self.height = 4
        self.pitch = 15
        self.yaw = 0
        camera.parent = self
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        mouse.locked = False

    def update(self):
        if mouse.right:
            self.yaw += mouse.velocity[0] * 50 * time.dt
            self.pitch -= mouse.velocity[1] * 50 * time.dt
            self.pitch = clamp(self.pitch, -30, 60)

        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        offset = Vec3(
            math.sin(yaw_rad) * math.cos(pitch_rad) * self.distance,
            math.sin(pitch_rad) * self.distance + self.height,
            math.cos(yaw_rad) * math.cos(pitch_rad) * self.distance
        )
        self.position = self.target.position + offset
        camera.look_at(self.target.position + Vec3(0, 1.5, 0))


# ── BASE BUILDER (unchanged) ──
class BaseBuilder:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.preview = None
        self.selected_type = 'wall'
        self.build_types = ['wall', 'tower', 'turret', 'generator', 'landing_pad']
        self.costs = {'wall': 50, 'tower': 200, 'turret': 300, 'generator': 150, 'landing_pad': 100}

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.create_preview()
            hud.set_message("BUILD MODE: Scroll types, Click to place, ESC to exit")
            mouse.locked = False
        else:
            if self.preview:
                destroy(self.preview)
                self.preview = None
            mouse.locked = False

    def create_preview(self):
        if self.preview:
            destroy(self.preview)
        colors = {'wall': color.gray, 'tower': color.blue, 'turret': color.red, 'generator': color.yellow, 'landing_pad': color.green}
        self.preview = Entity(
            model='cube',
            color=colors.get(self.selected_type, color.white),
            scale=(1, 2, 1) if self.selected_type == 'tower' else (2, 1, 2) if self.selected_type == 'landing_pad' else (1, 1, 1),
            alpha=0.5
        )

    def update(self):
        if not self.active:
            return
        ground = world.get_ground_height(self.player.x, self.player.z)
        self.preview.position = self.player.position + self.player.forward * 5
        self.preview.y = world.get_ground_height(self.preview.x, self.preview.z) + self.preview.scale_y / 2

    def place(self):
        if not self.active:
            return
        cost = self.costs.get(self.selected_type, 100)
        if self.player.credits < cost:
            hud.set_message(f"Need {cost} credits!")
            return
        self.player.credits -= cost
        b = Entity(
            model='cube',
            color=self.preview.color,
            position=self.preview.position,
            scale=self.preview.scale,
            collider='box'
        )
        self.player.bases.append({
            'type': self.selected_type,
            'pos': [b.x, b.y, b.z],
            'scale': [b.scale_x, b.scale_y, b.scale_z]
        })
        hud.set_message(f"Built {self.selected_type}!")

    def next_type(self):
        idx = self.build_types.index(self.selected_type)
        self.selected_type = self.build_types[(idx + 1) % len(self.build_types)]
        self.create_preview()
        hud.set_message(f"Building: {self.selected_type} ({self.costs.get(self.selected_type, 0)} CR)")


# ── HUD ──
class HUD(Entity):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.msg = ""
        self.msg_timer = 0
        self.build_menu = False
        self.quest_panel_visible = False
        self.skill_panel_visible = False
        self.story_panel_visible = False
        self.crafting_open = False

    def set_message(self, text, duration=3):
        self.msg = text
        self.msg_timer = duration

    def update(self):
        self.msg_timer -= time.dt
        if self.msg_timer < 0:
            self.msg = ""

    def input(self, key):
        # Weapon switching
        if key in '123456':
            msg = weapon_sys.switch(key)
            if msg:
                self.set_message(msg)
        if key == 'r':
            self.set_message(weapon_sys.reload())
        # Crafting
        if key == 'c':
            self.crafting_open = not self.crafting_open
            if self.crafting_open:
                self.set_message("CRAFTING: Press 1-8 to craft, C to close")
                mouse.locked = False
            else:
                mouse.locked = True
        if self.crafting_open and key in '12345678':
            crafting.craft(int(key) - 1)
        # Multiplayer
        if key == 'p':
            if multiplayer.enabled:
                multiplayer.disable()
                self.set_message("P2 disabled")
            else:
                multiplayer.enable()
                self.set_message("P2 joined! Arrow keys + Enter/RCtrl")
        # Skill tree
        if key == 'k':
            self.skill_panel_visible = not self.skill_panel_visible
            mouse.locked = self.skill_panel_visible
        # Story log
        if key == 'j':
            self.story_panel_visible = not self.story_panel_visible
            mouse.locked = self.story_panel_visible
        # Existing controls
        if key == 'b':
            base_builder.toggle()
        if key == 'tab up':
            base_builder.next_type()
        if key == 'left mouse down' and base_builder.active:
            base_builder.place()
        if key == 'e':
            self.interact_nearby()
        if key == 'v':
            self.summon_vehicle()
        if key == 'q' and self.quest_panel_visible:
            self.quest_panel_visible = False
            mouse.locked = True
        if key == 'm':
            self.mine()
        if key == 'f5':
            self.player.save()
            self.set_message("Game Saved!")
        if key == 'escape':
            if base_builder.active:
                base_builder.toggle()
                mouse.locked = True
            if self.quest_panel_visible:
                self.quest_panel_visible = False
                mouse.locked = True
            if self.skill_panel_visible:
                self.skill_panel_visible = False
                mouse.locked = True
            if self.story_panel_visible:
                self.story_panel_visible = False
                mouse.locked = True
            if self.crafting_open:
                self.crafting_open = False
                mouse.locked = True

    def summon_vehicle(self):
        """V = hoverbike; Shift+V = ship."""
        vtype = 'bike' if not held_keys['left shift'] else 'ship'
        # Create if doesn't exist
        if self.player.vehicle is None or self.player.vehicle.vtype != vtype:
            if self.player.vehicle:
                self.player.vehicle.dismiss()
            self.player.vehicle = Vehicle(vtype=vtype)
        # Summon near player
        self.player.vehicle.summon(self.player.position)
        if vtype == 'bike':
            self.player.vehicle.mount(self.player)
        self.set_message(f"{vtype.upper()} summoned! (E to interact with shops)")

    def interact_nearby(self):
        """E key – interact with nearby NPCs, shops, loot, dungeons, bosses, events."""
        pos = self.player.position
        # Dungeon exit (if active)
        global dungeon
        if dungeon and dungeon.active:
            for child in dungeon.root.children:
                if isinstance(child, PortalExit) and distance(pos, child.position) < 4:
                    msg = dungeon.exit_to_surface(self.player, sound_mgr)
                    self.set_message(msg, 3)
                    self.player.in_dungeon = False
                    dungeon = None
                    return
                if isinstance(child, Chest) and distance(pos, child.position) < 3:
                    msg = child.interact(self.player, sound_mgr)
                    self.set_message(msg, 2)
                    story_mgr.update('loot')
                    return
        # Dungeon entrance
        global dungeon_entrance
        if dungeon_entrance and distance(pos, dungeon_entrance.position) < 5:
            dungeon = Dungeon(dungeon_entrance.position)
            msg = dungeon.enter_dungeon(self.player, sound_mgr)
            self.player.in_dungeon = True
            self.set_message(msg, 3)
            story_mgr.update('discover', target='dungeon')
            return
        # Boss portals
        global boss_portals, boss_arena
        for bp in boss_portals:
            if distance(pos, bp.position) < 4 and boss_arena.active_boss is None:
                boss = boss_arena.spawn_boss(bp.position + Vec3(0, 2, 10), bp.btype)
                self.set_message(f"BOSS FIGHT: {bp.btype}!")
                story_mgr.update('discover', target='boss_arena')
                return
        # Event interactions (anomaly, caravan)
        for ev in event_sys.active_events:
            if ev['type'] == 'anomaly':
                core = ev.get('anomaly')
                if core and distance(pos, core.position) < 5:
                    val = getattr(core, 'value', 100)
                    rtype = getattr(core, 'reward_type', 'credits')
                    if rtype == 'credits':
                        self.player.credits += val
                    elif rtype == 'minerals':
                        self.player.minerals += val
                    elif rtype == 'xp':
                        self.player.xp += val
                    self.set_message(f"Anomaly scanned! +{val} {rtype}")
                    ev['remaining'] = 0
                    return
            if ev['type'] == 'trader_caravan':
                caravan = ev.get('caravan')
                if caravan and distance(pos, caravan.position) < 5:
                    self.open_caravan_ui(caravan)
                    return
        # Loot crates
        for crate in loot_mgr.crates:
            if not crate.opened and distance(pos, crate.position) < 3:
                crate.open(self.player, self, weapon_sys, skill_tree)
                story_mgr.update('loot')
                return
        # Shops / Quests (neutral cities)
        for city in world.cities:
            if city.faction != 'neutral':
                continue
            for shop in city.shops:
                if distance(pos, shop.position) < 6:
                    self.open_shop_ui(shop)
                    return
            for qg in city.quest_givers:
                if distance(pos, qg.position) < 6:
                    self.open_quest_dialog(qg)
                    return
        self.set_message("Nothing nearby to interact with.", 2)

    def open_caravan_ui(self, caravan):
        inv = getattr(caravan, 'shop_inventory', {})
        if not inv:
            self.set_message("Caravan inventory empty.")
            return
        items = list(inv.items())
        # Cycle through on repeated E presses
        idx = getattr(caravan, '_shop_idx', 0) % len(items)
        item_name, info = items[idx]
        if held_keys['left shift']:
            self.set_message(f"Caravan: {item_name} — Sell for {info.get('sell', 0)} CR (press E to cycle)")
        else:
            price = info.get('buy', 0)
            if self.player.credits >= price and info.get('stock', 0) > 0:
                self.player.credits -= price
                info['stock'] -= 1
                self.set_message(f"Bought {item_name}!")
            else:
                self.set_message(f"Need {price} CR for {item_name}")
        caravan._shop_idx = idx + 1

    def open_shop_ui(self, shop):
        """Simple buy/sell prompt."""
        self.set_message(f"Shop: {shop.city.name} | CR: {self.player.credits}")
        # For CLI simplicity: cycle through items by pressing E repeatedly
        # Press E to BUY first available item; Shift+E to SELL first item
        if held_keys['left shift']:
            success, msg = shop.trade(self.player, 'health_pack', 'sell')
            self.set_message(msg, 2.5)
        else:
            # Demo: buy health pack if affordable
            success, msg = shop.trade(self.player, 'health_pack', 'buy')
            self.set_message(msg, 2.5)

    def open_quest_dialog(self, qg):
        """Display quest offer or turn-in."""
        if qg.interact_cooldown > 0:
            return
        qg.interact_cooldown = 1.0

        quest = qg.offer_quest(self.player)
        if quest is None:
            self.set_message(f"{qg.name}: No quests right now. Explore and come back!", 4)
            return

        if quest['type'] == 'kill' and quest.get('current', 0) >= quest['amount']:
            # Complete kill quest
            quest['completed'] = True
            self.player.credits += quest['reward_cr']
            self.player.xp += quest['reward_xp']
            # Remove from active list
            if quest in self.player.active_quests:
                self.player.active_quests.remove(quest)
            self.set_message(f"QUEST COMPLETE! +{quest['reward_cr']} CR, +{quest['reward_xp']} XP", 4)
            return

        # Offer new quest
        self.player.active_quests.append(quest)
        self.set_message(f"NEW QUEST: {quest['desc']}  Rewards: {quest['reward_cr']} CR, {quest['reward_xp']} XP", 5)

    def scan_rom(self):
        roms = uni.get_roms()
        if roms:
            rom = random.choice(roms)
            rid = rom.get('id', rom.get('path', ''))
            if rid not in self.player.discovered_roms:
                self.player.discovered_roms.add(rid)
                name = rom.get('name', 'Unknown')[:35]
                self.set_message(f"DISCOVERED ROM: {name}")
                self.player.xp += 15
                self.player.credits += random.randint(20, 60)
                # Progress kill/fetch quests
                self._progress_quests('scan', 1)
            else:
                self.set_message("Sector already scanned.")
        else:
            self.set_message("No ROM database loaded.")

    def _progress_quests(self, qtype, amount=1):
        for q in self.player.active_quests:
            if q['type'] == qtype:
                q['current'] = q.get('current', 0) + amount

    def mine(self):
        amount = random.randint(5, 25) + getattr(self.player, 'mineral_bonus', 0)
        self.player.minerals += amount
        self._progress_quests('fetch', amount)
        self.set_message(f"Mined {amount} minerals")

    def draw(self):
        # HP + Shield Bar
        hp_pct = self.player.hp / self.player.max_hp
        hp_color = color.green if hp_pct > 0.5 else color.yellow if hp_pct > 0.25 else color.red
        Text(text=f"HP: {int(self.player.hp)}/{int(self.player.max_hp)}", position=(-0.95, 0.45), scale=1.5, color=hp_color)
        shield_pct = player.shield_strength / player.max_shield
        shield_color = color.cyan if shield_pct > 0.5 else color.blue
        Text(text=f"Shield: {int(player.shield_strength)}/{int(player.max_shield)}", position=(-0.95, 0.41), scale=1.2, color=shield_color)

        # Weapon info
        Text(text=weapon_sys.get_hud_text(), position=(-0.95, 0.37), scale=1.2, color=color.yellow)

        # Stats
        Text(text=f"Credits: {self.player.credits}  |  Minerals: {self.player.minerals}", position=(-0.95, 0.33), scale=1.2, color=color.white)
        Text(text=f"Level: {self.player.level}  |  XP: {self.player.xp}/{self.player.level*100}", position=(-0.95, 0.29), scale=1.2, color=color.white)
        Text(text=f"ROMs: {len(self.player.discovered_roms)}/362", position=(-0.95, 0.25), scale=1.2, color=color.cyan)
        Text(text=f"Skill Points: {skill_tree.points}", position=(-0.95, 0.21), scale=1.2, color=color.violet)

        # Weather / Story
        if weather_sys.weather != 'clear':
            Text(text=f"Weather: {weather_sys.weather.title()}", position=(0.6, 0.45), scale=1.2, color=color.light_gray)
        ch = story_mgr.get_current()
        if ch:
            Text(text=f"Chapter: {ch['title']}", position=(0.6, 0.40), scale=1, color=color.gold)

        # Exposure overlay
        if player.exposure > 0.05:
            overlay = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.rgba(100,100,120,int(player.exposure*100)), z=0.2)
            destroy(overlay, delay=0.05)

        # Build mode indicator
        if base_builder.active:
            Text(text=f"BUILD MODE: {base_builder.selected_type.upper()} ({base_builder.costs.get(base_builder.selected_type, 0)} CR)", position=(-0.95, 0.15), scale=1.5, color=color.yellow)
            Text(text="TAB: change type  |  CLICK: place  |  ESC: exit", position=(-0.95, 0.11), scale=1, color=color.gray)

        # Message
        if self.msg:
            Text(text=self.msg, position=(0, 0.35), origin=(0, 0), scale=2, color=color.yellow)

        # Time of day
        tod = day_night.time_of_day
        hours = int(tod * 24)
        mins = int((tod * 24 * 60) % 60)
        day_status = "DAY" if 6 <= hours < 20 else "NIGHT"
        Text(text=f"Time: {hours:02d}:{mins:02d}  [{day_status}]", position=(-0.95, 0.17), scale=1, color=color.white)

        # Panels
        if self.quest_panel_visible:
            self._draw_quest_log()
        if self.skill_panel_visible:
            self._draw_skill_tree()
        if self.story_panel_visible:
            self._draw_story_log()
        if self.crafting_open:
            self._draw_crafting_menu()

        # Controls
        Text(text="WASD: Move  |  SHIFT: Run  |  SPACE: Jump  |  MOUSE: Aim  |  L-CLICK: Shoot", position=(-0.95, -0.42), scale=0.8, color=color.gray)
        Text(text="1-6: Weapon  |  R: Reload  |  C: Craft  |  K: Skills  |  J: Story", position=(-0.95, -0.45), scale=0.8, color=color.gray)
        Text(text="B: Build  |  E: Interact  |  V: Vehicle  |  M: Mine  |  Q: Quests  |  P: P2  |  F5: Save", position=(-0.95, -0.48), scale=0.8, color=color.gray)

    def _draw_quest_log(self):
        bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.7), position=(0.6, 0), color=color.rgba(0, 0, 0, 200))
        Title = Text(text="ACTIVE QUESTS", position=(0.6, 0.28), scale=1.5, color=color.yellow, origin=(0, 0))
        y = 0.22
        if not self.player.active_quests:
            Text(text="No active quests.", position=(0.6, y), scale=1, color=color.gray, origin=(0, 0))
        for i, q in enumerate(self.player.active_quests):
            desc = q['desc'][:45]
            if q['type'] in ('kill', 'fetch'):
                cur = q.get('current', 0)
                total = q['amount']
                Text(text=f"{i+1}. {desc}", position=(0.35, y), scale=0.9, color=color.white, origin=(-0.5, 0))
                Text(text=f"({cur}/{total})", position=(0.8, y), scale=0.9, color=color.cyan, origin=(-0.5, 0))
            else:
                Text(text=f"{i+1}. {desc}", position=(0.35, y), scale=0.9, color=color.white, origin=(-0.5, 0))
            y -= 0.1
        Text(text="Press Q to close", position=(0.6, -0.32), scale=0.8, color=color.gray, origin=(0, 0))

    def _draw_skill_tree(self):
        bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.7), position=(0.6, 0), color=color.rgba(0, 0, 0, 200))
        Title = Text(text="SKILL TREE", position=(0.6, 0.28), scale=1.5, color=color.violet, origin=(0, 0))
        y = 0.22
        for key, s in skill_tree.SKILLS.items():
            r = skill_tree.ranks[key]
            status = f"[{r}/{s['max']}]" if r < s['max'] else "[MAX]"
            can = "●" if skill_tree.can_buy(key) else "○"
            Text(text=f"{can} {s['name']} {status} — {s['desc']}", position=(0.35, y), scale=0.8, color=color.white, origin=(-0.5, 0))
            y -= 0.06
        Text(text=f"Points: {skill_tree.points}  |  Press K to close", position=(0.6, -0.32), scale=0.8, color=color.gray, origin=(0, 0))

    def _draw_story_log(self):
        bg = Entity(parent=camera.ui, model='quad', scale=(0.6, 0.7), position=(0.6, 0), color=color.rgba(0, 0, 0, 200))
        lines = story_mgr.get_log().split('\n')
        y = 0.28
        for line in lines[:18]:
            col = color.gold if line.startswith('→') else color.white
            Text(text=line[:50], position=(0.35, y), scale=0.85, color=col, origin=(-0.5, 0))
            y -= 0.05
        Text(text="Press J to close", position=(0.6, -0.32), scale=0.8, color=color.gray, origin=(0, 0))

    def _draw_crafting_menu(self):
        bg = Entity(parent=camera.ui, model='quad', scale=(0.5, 0.6), position=(0, 0), color=color.rgba(0, 0, 0, 200))
        lines = crafting.get_menu().split('\n')
        y = 0.22
        for line in lines[:12]:
            Text(text=line[:45], position=(-0.2, y), scale=0.9, color=color.white, origin=(-0.5, 0))
            y -= 0.05
        Text(text="Press 1-8 to craft, C to close", position=(0, -0.28), scale=0.8, color=color.gray, origin=(0, 0))

    def input(self, key):
        super().input(key)
        if key == 'q' and not self.quest_panel_visible:
            self.quest_panel_visible = True
            mouse.locked = False


# ── SKY & LIGHTING ── (now managed by DayNightCycle entity above)


# ── CREATE ENTITIES ──
player = Player()
cam_ctrl = ThirdPersonCamera(player)
base_builder = BaseBuilder(player)
hud = HUD(player)

# New systems init
sound_mgr   = SoundManager(player.master_volume)
weapon_sys  = WeaponSystem(player)
skill_tree  = SkillTree(player)
crafting    = CraftingStation(player, hud)
story_mgr   = StoryManager(player, hud)
weather_sys = WeatherSystem(player)
event_sys   = RandomEventSystem(player, enemy_mgr, sound_mgr)
loot_mgr    = LootCrateManager(player, sound_mgr)
dungeon     = None
boss_arena  = BossArenaManager()
multiplayer = MultiplayerManager()
projectiles = []

# Link player to systems
player.hud = hud
player.weapon_sys = weapon_sys
player.skill_tree = skill_tree

# Spawn world content
loot_mgr.spawn_crates(player.position, count=20, radius=200)

# Dungeon entrance
dungeon_entrance = Entity(model='torus', color=color.violet, scale=3, position=Vec3(50, 5, 50), collider='box')

# Boss arena portals
boss_portals = []
for i, btype in enumerate(['Eldoria', 'Nebula Tyrant', 'Nexus Prime']):
    bp = Entity(model='ring', color=color.red, scale=2, position=Vec3(-50 - i*30, 5, -50), collider='box')
    bp.btype = btype
    boss_portals.append(bp)

# Load save after all systems exist
player.load_save()

# Spawn vehicles
bike = Vehicle(vtype='bike')
ship = Vehicle(vtype='ship')
player.vehicle = None  # no vehicle at start

# Initial enemy spawn near cities
for city in world.cities:
    if city.faction == 'enemy':
        enemy_mgr.spawn_enemies(Vec3(city.x, 5, city.z), 'high', 5)
    else:
        enemy_mgr.spawn_enemies(Vec3(city.x, 5, city.z), 'medium', 3)

# ── UPDATE LOOP ──
def update():
    if not getattr(player, "in_dungeon", False):
        world.update_chunks(player.x, player.z)

    is_night = day_night.update()
    enemy_mgr.update(player.position, time.dt, is_night=is_night)
    base_builder.update()

    # New system updates
    event_sys.update(time.dt)
    weather_sys.update()
    weapon_sys.update(time.dt)
    boss_arena.update(player, time.dt, hud)
    multiplayer.update(time.dt)
    loot_mgr.update()

    # Loot crate interaction
    loot_mgr.check_nearby(player, hud, weapon_sys, skill_tree)

    # Meteor collisions from events
    for m in event_sys.get_meteor_collisions():
        dmg = getattr(m, 'damage', 10)
        player.hp -= dmg
        hud.set_message(f"Meteor hit! -{dmg} HP")

    # Projectile updates
    for p in projectiles[:]:
        if not p['entity']:
            projectiles.remove(p)
            continue
        p['entity'].position += p['direction'] * p['speed'] * time.dt
        p['range_left'] -= p['speed'] * time.dt
        if p['range_left'] <= 0:
            destroy(p['entity'])
            projectiles.remove(p)
            continue
        hit = raycast(p['entity'].position, p['direction'], distance=0.5, ignore=[p['entity']])
        if hit.hit:
            if hasattr(hit.entity, 'take_damage'):
                hit.entity.take_damage(p['damage'])
                if hasattr(hit.entity, 'etype') and hit.entity.etype:
                    for q in player.active_quests:
                        if q['type'] == 'kill':
                            q['current'] = q.get('current', 0) + 1
                    story_mgr.update('kill', 1, hit.entity.etype)
            if p.get('explosive'):
                for e in enemy_mgr.enemies:
                    if distance(e.position, hit.world_point) < p['blast_radius']:
                        e.take_damage(p['damage'])
                exp = Entity(model='sphere', color=color.red, scale=0.5, position=hit.world_point)
                exp.animate_scale(p['blast_radius'], duration=0.3)
                destroy(exp, delay=0.3)
            destroy(p['entity'])
            projectiles.remove(p)

    # Shield regen
    if player.shield_strength < player.max_shield:
        player.shield_strength = min(player.max_shield, player.shield_strength + 2 * time.dt)

    # Vehicle: if mounted, player position follows vehicle
    if player.vehicle and player.vehicle.rider:
        player.position = player.vehicle.position + Vec3(0, 1, 0)
        player.rotation_y = player.vehicle.rotation_y
    else:
        # Free-fly normal controls
        ground_y = world.get_ground_height(player.x, player.z)
        if player.y <= ground_y + 1:
            player.y = ground_y + 1
            player.grounded = True
            player.y_velocity = 0
        else:
            player.grounded = False
            player.y_velocity -= 20 * time.dt
            player.y += player.y_velocity * time.dt

        # WASD movement
        move_dir = Vec3(0, 0, 0)
        if held_keys['w']:
            move_dir += camera.forward
        if held_keys['s']:
            move_dir -= camera.forward
        if held_keys['a']:
            move_dir -= camera.right
        if held_keys['d']:
            move_dir += camera.right
        move_dir.y = 0
        if move_dir.length() > 0:
            move_dir = move_dir.normalized()
            speed = player.run_speed if held_keys['left shift'] else player.speed
            player.position += move_dir * speed * time.dt
            player.angle = math.degrees(math.atan2(move_dir.x, move_dir.z))
            player.rotation_y = lerp(player.rotation_y, player.angle, 8 * time.dt)

        # Jump
        if held_keys['space'] and player.grounded:
            player.y_velocity = 8
            player.grounded = False

        # Shooting
        if mouse.left:
            player_shoot()

        # Fall off world
        if player.y < -20:
            player.position = (0, 20, 0)
            player.hp -= 10
            hud.set_message("Fell into void! Respawning...")

    # Level up
    if player.xp >= player.level * 100:
        player.level += 1
        player.xp = 0
        player.max_hp += 20
        player.hp = player.max_hp
        player.weapon_damage += 5
        hud.set_message(f"LEVEL UP! Level {player.level}")

    # Regen health slowly
    if player.hp < player.max_hp:
        player.hp = min(player.max_hp, player.hp + 0.5 * time.dt)

    # Update kill quest progress from enemy deaths (handled by EnemyManager; we hook via custom count)
    # (enemy_mgr tracks kills via the Enemy.die method; we need to count when enemies die near player)
    # This is handled by having QuestGiver count enemy kills globally


def player_shoot():
    origin = player.position + Vec3(0, 1.5, 0)
    direction = camera.forward
    projs = weapon_sys.fire(origin, direction)
    if not projs:
        return
    sound_mgr.play('shoot')
    for p in projs:
        beam = Entity(model='sphere', color=p['color'], scale=0.15, position=p['origin'])
        projectiles.append({
            'entity': beam,
            'direction': p['direction'],
            'speed': p['speed'],
            'damage': p['damage'],
            'range_left': p['range'],
            'explosive': p.get('explosive', False),
            'blast_radius': p.get('blast_radius', 0),
        })
    flash = Entity(model='sphere', color=color.yellow, scale=0.3, position=origin)
    destroy(flash, delay=0.05)


# ── START ──
hud.set_message("Welcome to Project Nexus. Explore. Build. Conquer.")
app.run()
