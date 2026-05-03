import random, math, os, json
from ursina import *
from noise import pnoise2
from universe import Universe

uni = Universe()

# ── TEXTURE PATHS ──
# Use N64 textures from the OOT mod pack
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTURE_DIR = os.path.join(GAME_DIR, 'textures')
HylianTextureBase = TEXTURE_DIR

# Prefer bundled copies; fall back to source
TERRAIN_TEXTURE_1 = os.path.join(TEXTURE_DIR, 'hyrule_floor.png')
TERRAIN_TEXTURE_2 = os.path.join(TEXTURE_DIR, 'hyrule_floor_2.png')
if not os.path.exists(TERRAIN_TEXTURE_1) and os.path.exists(HylianTextureBase):
    # Pick first two PNGs found in the source Floor folder
    pngs = sorted([f for f in os.listdir(HylianTextureBase) if f.endswith('.png')])
    if len(pngs) >= 2:
        TERRAIN_TEXTURE_1 = os.path.join(HylianTextureBase, pngs[0])
        TERRAIN_TEXTURE_2 = os.path.join(HylianTextureBase, pngs[1])
ALT_TEXTURE = TERRAIN_TEXTURE_2


class TerrainChunk(Entity):
    def __init__(self, x_pos, z_pos, size=40, resolution=20):
        super().__init__()
        self.x_pos = x_pos
        self.z_pos = z_pos
        self.size = size
        self.res = resolution
        self.verts = []
        self.tris = []
        self.uvs = []
        self.norms = []

        step = size / resolution
        for z in range(resolution + 1):
            for x in range(resolution + 1):
                wx = x_pos + x * step
                wz = z_pos + z * step
                h = self.get_height(wx, wz)
                self.verts.append(Vec3(x * step - size / 2, h, z * step - size / 2))
                self.uvs.append(Vec2(x / resolution, z / resolution))
                self.norms.append(Vec3(0, 1, 0))

        for z in range(resolution):
            for x in range(resolution):
                i = z * (resolution + 1) + x
                self.tris.extend([i, i + 1, i + resolution + 1])
                self.tris.extend([i + 1, i + resolution + 2, i + resolution + 1])

        self.model = Mesh(vertices=self.verts, triangles=self.tris, uvs=self.uvs, normals=self.norms, mode='triangle')
        # Use N64 overworld floor textures if available, else fall back to Ursina's 'grass'
        if os.path.exists(TERRAIN_TEXTURE_1):
            self.texture = TERRAIN_TEXTURE_1
        else:
            self.texture = 'grass'
        self.collider = 'mesh'
        self.position = (x_pos + size / 2, 0, z_pos + size / 2)

    def get_height(self, x, z):
        scale = 0.02
        h = pnoise2(x * scale, z * scale, octaves=4) * 8
        h += pnoise2(x * scale * 2 + 100, z * scale * 2 + 100, octaves=2) * 3
        return max(-5, h)


class Building(Entity):
    def __init__(self, pos, btype='house', faction='neutral'):
        colors = {
            'house': color.rgb(180, 150, 100),
            'tower': color.rgb(120, 120, 140),
            'factory': color.rgb(80, 80, 90),
            'base': color.rgb(100, 200, 100),
            'enemy': color.rgb(200, 60, 60),
            'shop': color.rgb(60, 120, 200),
            'tavern': color.rgb(160, 100, 60),
        }
        scales = {
            'house': (2, 2, 2),
            'tower': (1.5, 6, 1.5),
            'factory': (4, 3, 4),
            'base': (3, 2, 3),
            'enemy': (2, 2.5, 2),
            'shop': (2.5, 2.5, 2),
            'tavern': (3, 2.5, 3),
        }
        super().__init__(
            model='cube',
            color=colors.get(btype, color.white),
            position=pos,
            scale=scales.get(btype, (2, 2, 2)),
            collider='box'
        )
        self.btype = btype
        self.faction = faction


# ── QUEST GIVER NPC ──
class QuestGiver(Entity):
    """Interactive NPC that offers repeatable fetch/kill quests."""
    def __init__(self, pos, name='QuestGiver', city=None):
        super().__init__(
            model='cube',
            color=color.rgb(200, 180, 80),
            position=pos,
            scale=(1, 2, 1),
            collider='box'
        )
        self.name = name
        self.city = city
        self.quests = self._generate_quests()
        self.greeting = random.choice([
            "Hey, traveler! Need some work?",
            "Got a moment? I have a job for you.",
            "You look capable. Interested in a quest?",
        ])
        self.has_new_quest = True
        self.interact_cooldown = 0
        self.speech_bubble = None

    def _generate_quests(self):
        types = ['fetch', 'kill', 'scan']
        quests = []
        for _ in range(random.randint(2, 4)):
            qtype = random.choice(types)
            if qtype == 'fetch':
                quests.append({
                    'type': 'fetch',
                    'desc': f"Bring me {random.randint(5, 20)} minerals from the field.",
                    'target': 'minerals',
                    'amount': random.randint(5, 20),
                    'reward_cr': random.randint(100, 300),
                    'reward_xp': random.randint(30, 80),
                    'completed': False
                })
            elif qtype == 'kill':
                quests.append({
                    'type': 'kill',
                    'desc': f"Eliminate {random.randint(3, 8)} enemies near {self.city.name if self.city else 'the area'}.",
                    'target': 'kills',
                    'amount': random.randint(3, 8),
                    'current': 0,
                    'reward_cr': random.randint(150, 400),
                    'reward_xp': random.randint(50, 100),
                    'completed': False
                })
            else:
                quests.append({
                    'type': 'scan',
                    'desc': "Scan a ROM sector from orbit.",
                    'target': 'scan',
                    'amount': 1,
                    'reward_cr': random.randint(80, 200),
                    'reward_xp': random.randint(20, 50),
                    'completed': False
                })
        return quests

    def offer_quest(self, player):
        """Return an available quest or None."""
        for q in self.quests:
            if not q['completed']:
                # For kill quests, check progress
                if q['type'] == 'kill' and q.get('current', 0) >= q['amount']:
                    return q
                elif q['type'] != 'kill':
                    return q
        return None

    def update(self):
        if self.interact_cooldown > 0:
            self.interact_cooldown -= time.dt
        # Bob up and down slightly for visibility
        self.y += math.sin(time.time() * 2) * 0.005


# ── TRADING SHOP ──
class Shop(Entity):
    """Neutral-city shop where player can buy and sell."""
    def __init__(self, pos, city):
        super().__init__(
            model='cube',
            color=color.rgb(60, 120, 200),
            position=pos,
            scale=(2.5, 2, 2),
            collider='box'
        )
        self.city = city
        # Inventory: item -> {price_buy, price_sell, stock}
        self.inventory = {
            'health_pack':  {'buy': 50,  'sell': 20,  'stock': 10, 'desc': 'Restores 50 HP'},
            'ammo_clip':    {'buy': 30,  'sell': 10,  'stock': 20, 'desc': '15 extra shots'},
            'armor_plate':  {'buy': 150, 'sell': 60,  'stock': 5,  'desc': '+20 max HP'},
            'mining_drill': {'buy': 100, 'sell': 40,  'stock': 8,  'desc': '+5 mineral yield'},
            'scope':        {'buy': 200, 'sell': 80,  'stock': 3,  'desc': 'Longer scan range'},
        }
        self.greeting = "Welcome! Buying or selling today?"

    def trade(self, player, item, action='buy'):
        """Execute a buy/sell transaction. Returns (success, msg)."""
        if item not in self.inventory:
            return False, "I don't stock that."
        entry = self.inventory[item]

        if action == 'buy':
            cost = entry['buy']
            if player.credits < cost:
                return False, f"Need {cost} credits."
            if entry['stock'] <= 0:
                return False, "Out of stock!"
            player.credits -= cost
            entry['stock'] -= 1
            # Grant item effects
            if item == 'health_pack':
                player.hp = min(player.max_hp, player.hp + 50)
            elif item == 'ammo_clip':
                player.weapon_damage += 2  # placeholder: shots not tracked
            elif item == 'armor_plate':
                player.max_hp += 20
                player.hp += 20
            elif item == 'mining_drill':
                player.mineral_bonus = getattr(player, 'mineral_bonus', 0) + 5
            elif item == 'scope':
                player.scan_range = getattr(player, 'scan_range', 100) + 50
            return True, f"Bought {item} for {cost} CR."

        elif action == 'sell':
            value = entry['sell']
            player.credits += value
            entry['stock'] += 1
            return True, f"Sold {item} for {value} CR."


# ── VEHICLE ENTITY ──
class Vehicle(Entity):
    """Player-summoned hoverbike / ship for fast travel."""
    def __init__(self, vtype='bike'):
        super().__init__(
            model='cube',
            color=color.rgb(80, 80, 200) if vtype == 'bike' else color.rgb(40, 40, 80),
            scale=(1, 0.5, 2) if vtype == 'bike' else (2, 0.8, 4),
            position=(0, -100, 0),  # start hidden below ground
            collider='box'
        )
        self.vtype = vtype
        self.speed = 25 if vtype == 'bike' else 40
        self.active = False
        self.rider = None  # player entity when mounted

    def summon(self, target_pos):
        """Appear near the target position."""
        self.position = target_pos + Vec3(0, 3, 0)
        self.active = True
        self.visible = True

    def dismiss(self):
        """Hide the vehicle."""
        self.position = Vec3(0, -100, 0)
        self.active = False
        self.visible = False
        self.rider = None

    def mount(self, player):
        """Player enters vehicle; camera follows vehicle."""
        self.rider = player
        player.visible = False  # hide player model
        player.position = self.position + Vec3(0, 1, 0)

    def dismount(self, player):
        """Player exits vehicle."""
        if self.rider:
            self.rider.visible = True
            self.rider.position = self.position + Vec3(2, 0, 0)
        self.rider = None

    def update(self):
        if not self.active or not self.rider:
            return
        # Vehicle follows player camera direction when summoned
        # Controls: WASD moves the vehicle, rider is carried
        move = Vec3(
            (held_keys['d'] - held_keys['a']),
            0,
            (held_keys['w'] - held_keys['s'])
        )
        if move.length() > 0:
            move = move.normalized()
            self.position += move * self.speed * time.dt
            self.rotation_y = self.rider.rotation_y


# ── CITY with integrated features ──
class City:
    def __init__(self, x, z, name, faction='neutral', size=5):
        self.x = x
        self.z = z
        self.name = name
        self.faction = faction
        self.size = size
        self.buildings = []
        self.quest_givers = []
        self.shops = []
        self.generate()

    def generate(self):
        building_types = ['house', 'house', 'tower', 'factory']
        if self.faction == 'neutral':
            building_types.extend(['shop', 'tavern'])

        for i in range(self.size):
            bx = self.x + random.uniform(-25, 25)
            bz = self.z + random.uniform(-25, 25)
            btype = random.choice(building_types)
            b = Building((bx, 5, bz), btype, self.faction)
            self.buildings.append(b)

        # Central tower
        tower = Building((self.x, 8, self.z), 'tower', self.faction)
        self.buildings.append(tower)

        # Neutral cities get a quest giver and a shop
        if self.faction == 'neutral':
            qg = QuestGiver(
                pos=(self.x + random.uniform(-5, 5), 5, self.z + random.uniform(-5, 5)),
                name=f"{self.name}_Guide",
                city=self
            )
            self.quest_givers.append(qg)
            shop = Shop(
                pos=(self.x + random.uniform(-10, 10), 5, self.z + random.uniform(-10, 10)),
                city=self
            )
            self.shops.append(shop)


class World:
    def __init__(self):
        self.chunks = {}
        self.cities = []
        self.pois = []
        self.enemy_spawns = []
        self.chunk_size = 40
        self.render_dist = 3
        self.player_chunk = (0, 0)
        self.generate_cities()
        self.generate_pois()

    def generate_cities(self):
        galaxy_names = [g["name"] for g in uni.galaxies[:4]]
        for i, gname in enumerate(galaxy_names):
            x = random.randint(-100, 120)
            z = random.randint(-100, 120)
            city = City(x, z, f"{gname}_City", faction='neutral', size=random.randint(3, 8))
            self.cities.append(city)
        # Enemy outposts
        for i in range(3):
            x = random.randint(-150, 150)
            z = random.randint(-150, 150)
            outpost = City(x, z, f"Outpost_{i}", faction='enemy', size=3)
            self.cities.append(outpost)

    def generate_pois(self):
        for i in range(15):
            x = random.randint(-200, 200)
            z = random.randint(-200, 200)
            self.pois.append({
                "x": x, "z": z,
                "name": f"Site_{i}",
                "type": random.choice(['ruins', 'crash', 'anomaly', 'mine', 'rom_cache']),
                "discovered": False
            })

    def update_chunks(self, px, pz):
        cx = int(px // self.chunk_size)
        cz = int(pz // self.chunk_size)
        if (cx, cz) == self.player_chunk:
            return
        self.player_chunk = (cx, cz)

        # Load nearby chunks
        for dx in range(-self.render_dist, self.render_dist + 1):
            for dz in range(-self.render_dist, self.render_dist + 1):
                key = (cx + dx, cz + dz)
                if key not in self.chunks:
                    chunk = TerrainChunk(
                        (cx + dx) * self.chunk_size,
                        (cz + dz) * self.chunk_size,
                        self.chunk_size,
                        12
                    )
                    self.chunks[key] = chunk

        # Unload distant chunks
        to_remove = []
        for key, chunk in self.chunks.items():
            if abs(key[0] - cx) > self.render_dist + 1 or abs(key[1] - cz) > self.render_dist + 1:
                to_remove.append(key)
                destroy(chunk)
        for key in to_remove:
            del self.chunks[key]

    def get_ground_height(self, x, z):
        scale = 0.02
        h = pnoise2(x * scale, z * scale, octaves=4) * 8
        h += pnoise2(x * scale * 2 + 100, z * scale * 2 + 100, octaves=2) * 3
        return max(-5, h)

    def get_nearest_city(self, pos, max_dist=50):
        best = None
        best_d = 1e9
        for city in self.cities:
            d = distance(Vec3(city.x, 0, city.z), Vec3(pos.x, 0, pos.z))
            if d < best_d:
                best_d = d
                best = city
        if best_d <= max_dist:
            return best
        return None
