#!/usr/bin/env python3
"""
Project Nexus: Space Universe
A standalone PC game built from 362 ROMs, AI-generated worlds, and N64 textures.
"""
import pygame
import random, math, os, json
from universe import Universe

# ── INIT ──
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project Nexus: Space Universe")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
font_big = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 20)

# ── COLORS ──
C_BLACK = (5, 5, 15)
C_STAR = (200, 200, 255)
C_PLAYER = (0, 255, 150)
C_ENEMY = (255, 60, 60)
C_LASER = (0, 255, 255)
C_TEXT = (240, 240, 240)
C_GALAXY = {
    "Zelda_Galaxy": (100, 200, 100),
    "Mario_Galaxy": (255, 200, 50),
    "Pokemon_Galaxy": (255, 100, 200),
    "Starfox_Galaxy": (100, 150, 255),
    "Racing_Galaxy": (255, 100, 50),
    "RPG_Galaxy": (150, 100, 255),
    "Horror_Galaxy": (150, 50, 50),
    "Fighting_Galaxy": (255, 180, 100),
}

# ── UNIVERSE ──
uni = Universe()
for g in uni.galaxies:
    g["x"] = random.randint(200, WIDTH - 200)
    g["y"] = random.randint(150, HEIGHT - 150)

# ── PLAYER ──
player = {
    "x": WIDTH // 2, "y": HEIGHT // 2,
    "vx": 0, "vy": 0,
    "angle": 0,
    "hp": 100, "max_hp": 100,
    "credits": 1000,
    "xp": 0, "level": 1,
    "weapon": "laser", "weapon_dmg": 10,
    "inventory": [],
    "discovered_roms": set(),
    "bases": [],
    "minerals": 0,
    "active_pokemon": None,
}

# Load saved state if exists
save_path = os.path.expanduser("~/HylianModding/Game/save.json")
if os.path.exists(save_path):
    try:
        with open(save_path) as f:
            s = json.load(f)
            player.update({k: v for k, v in s.items() if k in player})
            player["discovered_roms"] = set(player.get("discovered_roms", []))
    except Exception:
        pass

# ── GAME STATE ──
STATE_GALAXY_MAP = 0
STATE_ZONE = 1
STATE_COMBAT = 2
STATE_BASE = 3
state = STATE_GALAXY_MAP
current_galaxy = None
current_zone = None
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random()) for _ in range(200)]
enemies = []
lasers = []
particles = []
message = ""
message_timer = 0
scan_pulse = 0

# ── UTILS ──
def draw_text(surf, text, pos, color=C_TEXT, f=font, center=False):
    txt = f.render(str(text), True, color)
    r = txt.get_rect()
    r.topleft = pos
    if center:
        r.center = pos
    surf.blit(txt, r)

def distance(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

def save_game():
    s = {k: v for k, v in player.items()}
    s["discovered_roms"] = list(s["discovered_roms"])
    with open(save_path, "w") as f:
        json.dump(s, f)

def set_message(text, duration=180):
    global message, message_timer
    message = text
    message_timer = duration

# ── DRAWING ──
def draw_stars(surf, scroll_x=0, scroll_y=0):
    for sx, sy, brightness in stars:
        bx = (sx - scroll_x * 0.3) % WIDTH
        by = (sy - scroll_y * 0.3) % HEIGHT
        c = int(100 + 155 * brightness)
        pygame.draw.circle(surf, (c, c, c), (int(bx), int(by)), int(1 + brightness * 2))

def draw_ship(surf, x, y, angle, color, size=12):
    pts = []
    for i in range(3):
        a = math.radians(angle + i * 120)
        pts.append((x + math.cos(a) * size, y + math.sin(a) * size))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, (255, 255, 255), pts, 2)

def draw_galaxy_map():
    screen.fill(C_BLACK)
    draw_stars(screen)

    # Draw connection lines
    for i, g1 in enumerate(uni.galaxies):
        for g2 in uni.galaxies[i + 1:]:
            pygame.draw.line(screen, (40, 40, 60), (g1["x"], g1["y"]), (g2["x"], g2["y"]), 1)

    # Draw galaxies
    mx, my = pygame.mouse.get_pos()
    for g in uni.galaxies:
        col = C_GALAXY.get(g["name"], (150, 150, 150))
        r = 20 + g.get("total_zones", 5) * 2
        pygame.draw.circle(screen, col, (g["x"], g["y"]), r)
        pygame.draw.circle(screen, (255, 255, 255), (g["x"], g["y"]), r, 2)
        draw_text(screen, g["name"].replace("_", " "), (g["x"], g["y"] + r + 10), col, font_small, center=True)
        draw_text(screen, f"{g.get('total_zones', 0)} zones", (g["x"], g["y"] + r + 24), (150, 150, 150), font_small, center=True)

        if math.hypot(mx - g["x"], my - g["y"]) < r:
            draw_text(screen, f"Danger: {g.get('danger_level', 'medium')}", (g["x"], g["y"] - r - 20), (255, 200, 100), font_small, center=True)

    # UI panel
    pygame.draw.rect(screen, (20, 20, 30), (10, 10, 260, 140))
    pygame.draw.rect(screen, (100, 100, 150), (10, 10, 260, 140), 2)
    draw_text(screen, "PROJECT NEXUS", (20, 15), (0, 255, 150), font_big)
    draw_text(screen, f"HP: {player['hp']}/{player['max_hp']}", (20, 55))
    draw_text(screen, f"Credits: {player['credits']}", (20, 75))
    draw_text(screen, f"Level: {player['level']}  XP: {player['xp']}", (20, 95))
    draw_text(screen, f"ROMs Found: {len(player['discovered_roms'])}/362", (20, 115), (100, 200, 255))

    # Companion
    if player["active_pokemon"]:
        p = player["active_pokemon"]
        pygame.draw.rect(screen, (30, 20, 40), (WIDTH - 210, 10, 200, 80))
        pygame.draw.rect(screen, (200, 100, 255), (WIDTH - 210, 10, 200, 80), 2)
        draw_text(screen, f"Companion: {p['name']}", (WIDTH - 200, 15), (255, 150, 255))
        draw_text(screen, f"Type: {p.get('element', '?')}  Loyalty: {p.get('loyalty', 0)}", (WIDTH - 200, 35), (200, 200, 200), font_small)
        draw_text(screen, f"Ability: {p.get('space_ability', '?')}", (WIDTH - 200, 50), (200, 200, 200), font_small)

    # Controls
    draw_text(screen, "Click galaxy to enter  |  B = Bases  |  S = Save", (20, HEIGHT - 30), (150, 150, 150), font_small)

def draw_zone():
    screen.fill(C_BLACK)
    scroll_x, scroll_y = player["x"] - WIDTH // 2, player["y"] - HEIGHT // 2
    draw_stars(screen, scroll_x, scroll_y)

    # Zone name
    if current_zone:
        draw_text(screen, f"{current_zone.get('name', 'Unknown')} — {current_zone.get('galaxy', '')}", (WIDTH // 2, 30), C_TEXT, font_big, center=True)
        draw_text(screen, f"Danger: {current_zone.get('danger_level', 'medium')}  Boss: {'YES' if current_zone.get('boss_present') else 'NO'}", (WIDTH // 2, 60), (255, 100, 100) if current_zone.get('boss_present') else (150, 150, 150), font_small, center=True)

    # Draw enemies
    for e in enemies:
        draw_ship(screen, e["x"] - scroll_x + WIDTH // 2, e["y"] - scroll_y + HEIGHT // 2, e.get("angle", 0), e["color"], 10)
        # HP bar
        bar_x = e["x"] - scroll_x + WIDTH // 2 - 15
        bar_y = e["y"] - scroll_y + HEIGHT // 2 - 18
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, 30, 4))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, 30 * (e["hp"] / e.get("max_hp", e["hp"])), 4))

    # Draw lasers
    for l in lasers:
        lx = l["x"] - scroll_x + WIDTH // 2
        ly = l["y"] - scroll_y + HEIGHT // 2
        pygame.draw.line(screen, C_LASER, (lx, ly), (lx - math.cos(l["angle"]) * 15, ly - math.sin(l["angle"]) * 15), 3)

    # Draw particles
    for p in particles:
        px = p["x"] - scroll_x + WIDTH // 2
        py = p["y"] - scroll_y + HEIGHT // 2
        pygame.draw.circle(screen, p["color"], (int(px), int(py)), int(p["life"] / 10))

    # Draw player
    draw_ship(screen, WIDTH // 2, HEIGHT // 2, player["angle"], C_PLAYER, 14)

    # Draw companion following
    if player["active_pokemon"]:
        follow_dist = 30
        fx = WIDTH // 2 - math.cos(math.radians(player["angle"])) * follow_dist
        fy = HEIGHT // 2 - math.sin(math.radians(player["angle"])) * follow_dist
        col = {"electric": (255, 255, 0), "fire": (255, 100, 0), "water": (0, 100, 255), "grass": (0, 255, 0), "psychic": (255, 0, 255), "dragon": (150, 0, 255), "space": (200, 200, 255)}.get(player["active_pokemon"].get("element", ""), (200, 200, 200))
        pygame.draw.circle(screen, col, (int(fx), int(fy)), 8)
        pygame.draw.circle(screen, (255, 255, 255), (int(fx), int(fy)), 8, 2)

    # Scan pulse
    global scan_pulse
    scan_pulse = (scan_pulse + 2) % 200
    pygame.draw.circle(screen, (0, 255, 150), (WIDTH // 2, HEIGHT // 2), scan_pulse, 1)

    # UI
    pygame.draw.rect(screen, (20, 20, 30), (10, HEIGHT - 80, 300, 70))
    pygame.draw.rect(screen, (100, 100, 150), (10, HEIGHT - 80, 300, 70), 2)
    draw_text(screen, f"HP: {player['hp']}  CR: {player['credits']}", (20, HEIGHT - 75))
    draw_text(screen, f"Minerals: {player['minerals']}  Bases: {len(player['bases'])}", (20, HEIGHT - 55), font=font_small)
    draw_text(screen, "WASD/Arrows: Move  |  SPACE: Shoot  |  E: Scan ROM  |  M: Mine  |  B: Base  |  TAB: Exit", (20, HEIGHT - 35), (150, 150, 150), font_small)

def draw_base_menu():
    screen.fill(C_BLACK)
    draw_stars(screen)
    draw_text(screen, "NEXUS COMMAND STATION", (WIDTH // 2, 50), (0, 255, 150), font_big, center=True)

    y = 120
    options = [
        ("1. Build Base", f"Cost: 500 CR  |  You have: {player['credits']} CR"),
        ("2. Upgrade Ship", f"Cost: 300 CR  |  Weapon: {player['weapon_dmg']} dmg"),
        ("3. Factory Production", f"Minerals: {player['minerals']}  |  Converts to credits"),
        ("4. Heal", f"Cost: 100 CR  |  HP: {player['hp']}/{player['max_hp']}"),
        ("5. Scan ROM Database", f"Found: {len(player['discovered_roms'])}/362"),
        ("6. Summon Companion", f"Available: {len(uni.companions)} Pokemon"),
    ]
    for title, desc in options:
        pygame.draw.rect(screen, (30, 30, 40), (WIDTH // 2 - 300, y, 600, 50))
        pygame.draw.rect(screen, (100, 100, 150), (WIDTH // 2 - 300, y, 600, 50), 2)
        draw_text(screen, title, (WIDTH // 2 - 280, y + 5), (200, 200, 255))
        draw_text(screen, desc, (WIDTH // 2 - 280, y + 28), (150, 150, 150), font_small)
        y += 60

    draw_text(screen, "Press 1-6 to select  |  TAB to return", (WIDTH // 2, HEIGHT - 40), (150, 150, 150), font_small, center=True)

def draw_message():
    global message_timer
    if message_timer > 0:
        message_timer -= 1
        alpha = min(255, message_timer * 2)
        s = pygame.Surface((WIDTH, 40))
        s.set_alpha(alpha)
        s.fill((20, 20, 40))
        screen.blit(s, (0, HEIGHT // 2 - 20))
        draw_text(screen, message, (WIDTH // 2, HEIGHT // 2 - 10), (0, 255, 150), font_big, center=True)

# ── LOGIC ──
def spawn_enemies(zone):
    global enemies
    enemies = []
    count = random.randint(2, 5)
    danger = zone.get("danger_level", "medium")
    for _ in range(count):
        e = uni.get_random_enemy(danger)
        e["x"] = player["x"] + random.randint(-400, 400)
        e["y"] = player["y"] + random.randint(-400, 400)
        e["max_hp"] = e["hp"]
        e["angle"] = random.randint(0, 360)
        enemies.append(e)

def update_zone(dt):
    keys = pygame.key.get_pressed()
    accel = 0.3
    max_speed = 6
    friction = 0.96

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player["vx"] += math.cos(math.radians(player["angle"])) * accel
        player["vy"] += math.sin(math.radians(player["angle"])) * accel
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player["vx"] -= math.cos(math.radians(player["angle"])) * accel * 0.5
        player["vy"] -= math.sin(math.radians(player["angle"])) * accel * 0.5
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player["angle"] -= 4
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player["angle"] += 4

    speed = math.hypot(player["vx"], player["vy"])
    if speed > max_speed:
        player["vx"] = player["vx"] / speed * max_speed
        player["vy"] = player["vy"] / speed * max_speed
    player["vx"] *= friction
    player["vy"] *= friction
    player["x"] += player["vx"]
    player["y"] += player["vy"]

    # Update enemies
    for e in enemies:
        dx = player["x"] - e["x"]
        dy = player["y"] - e["y"]
        dist = math.hypot(dx, dy)
        if dist > 10:
            e["x"] += (dx / dist) * e["speed"] * 0.5
            e["y"] += (dy / dist) * e["speed"] * 0.5
            e["angle"] = math.degrees(math.atan2(dy, dx))
        # Attack player
        if dist < 20:
            player["hp"] -= 1
            if player["hp"] <= 0:
                set_message("CRITICAL FAILURE — Respawning at base...")
                player["hp"] = player["max_hp"]
                player["x"], player["y"] = 0, 0

    # Update lasers
    for l in lasers[:]:
        l["x"] += math.cos(l["angle"]) * 12
        l["y"] += math.sin(l["angle"]) * 12
        l["life"] -= 1
        if l["life"] <= 0:
            lasers.remove(l)
            continue
        # Hit enemies
        for e in enemies[:]:
            if distance(l, e) < 15:
                e["hp"] -= l["dmg"]
                # Particles
                for _ in range(5):
                    particles.append({"x": e["x"], "y": e["y"], "vx": random.uniform(-2, 2), "vy": random.uniform(-2, 2), "life": 30, "color": e["color"]})
                if l in lasers:
                    lasers.remove(l)
                if e["hp"] <= 0:
                    set_message(f"Destroyed {e['name']}!")
                    player["credits"] += random.randint(10, 50)
                    player["xp"] += random.randint(5, 15)
                    if player["xp"] >= player["level"] * 100:
                        player["level"] += 1
                        player["xp"] = 0
                        set_message(f"LEVEL UP! Now level {player['level']}")
                    enemies.remove(e)
                break

    # Update particles
    for p in particles[:]:
        p["x"] += p.get("vx", 0)
        p["y"] += p.get("vy", 0)
        p["life"] -= 2
        if p["life"] <= 0:
            particles.remove(p)

    # Companion auto-attack
    if player["active_pokemon"] and enemies:
        nearest = min(enemies, key=lambda e: distance(player, e))
        if distance(player, nearest) < 200 and random.random() < 0.02:
            lasers.append({
                "x": player["x"] - math.cos(math.radians(player["angle"])) * 30,
                "y": player["y"] - math.sin(math.radians(player["angle"])) * 30,
                "angle": math.atan2(nearest["y"] - player["y"], nearest["x"] - player["x"]),
                "dmg": 5 + player["active_pokemon"].get("evolution_level", 1) * 3,
                "life": 60,
                "source": "companion"
            })

def scan_rom():
    roms = uni.get_roms()
    if roms:
        rom = random.choice(roms)
        rom_id = rom.get("id", rom.get("path", ""))
        if rom_id not in player["discovered_roms"]:
            player["discovered_roms"].add(rom_id)
            name = rom.get("name", "Unknown ROM")
            set_message(f"DISCOVERED: {name[:40]}")
            player["xp"] += 10
        else:
            set_message("Already scanned this sector.")
    else:
        set_message("No ROM signatures detected.")

def mine():
    amount = random.randint(5, 20)
    player["minerals"] += amount
    set_message(f"Mined {amount} minerals.")

def base_action(key):
    if key == pygame.K_1:
        if player["credits"] >= 500:
            player["credits"] -= 500
            player["bases"].append({"x": player["x"], "y": player["y"], "level": 1})
            set_message("Base constructed!")
        else:
            set_message("Not enough credits!")
    elif key == pygame.K_2:
        if player["credits"] >= 300:
            player["credits"] -= 300
            player["weapon_dmg"] += 5
            set_message(f"Ship upgraded! Weapon damage: {player['weapon_dmg']}")
        else:
            set_message("Not enough credits!")
    elif key == pygame.K_3:
        if player["minerals"] >= 10:
            produced = player["minerals"] // 10 * 50
            player["credits"] += produced
            player["minerals"] = player["minerals"] % 10
            set_message(f"Factory produced {produced} credits.")
        else:
            set_message("Need more minerals (10 per batch).")
    elif key == pygame.K_4:
        if player["credits"] >= 100 and player["hp"] < player["max_hp"]:
            player["credits"] -= 100
            player["hp"] = min(player["max_hp"], player["hp"] + 30)
            set_message("Ship repaired.")
        else:
            set_message("Already at full health or no credits.")
    elif key == pygame.K_5:
        roms = uni.get_roms()
        if roms:
            undiscovered = [r for r in roms if r.get("id", r.get("path", "")) not in player["discovered_roms"]]
            if undiscovered:
                for r in random.sample(undiscovered, min(5, len(undiscovered))):
                    player["discovered_roms"].add(r.get("id", r.get("path", "")))
                set_message(f"Database scan complete. Found {len(player['discovered_roms'])}/362 ROMs.")
            else:
                set_message("All 362 ROMs discovered! Universe complete.")
    elif key == pygame.K_6:
        if uni.companions:
            c = random.choice(uni.companions)
            player["active_pokemon"] = c
            set_message(f"{c['name']} joined your fleet!")
        else:
            set_message("No companions available.")

# ── MAIN LOOP ──
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            save_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if state == STATE_GALAXY_MAP:
                    pass
                elif state == STATE_BASE:
                    state = STATE_ZONE if current_zone else STATE_GALAXY_MAP
                else:
                    state = STATE_GALAXY_MAP
                    current_zone = None
                    enemies = []
            if event.key == pygame.K_s and state == STATE_GALAXY_MAP:
                save_game()
                set_message("Game saved.")
            if event.key == pygame.K_b:
                if state == STATE_BASE:
                    state = STATE_ZONE if current_zone else STATE_GALAXY_MAP
                else:
                    state = STATE_BASE
            if state == STATE_BASE:
                base_action(event.key)
            if state == STATE_ZONE:
                if event.key == pygame.K_SPACE:
                    lasers.append({
                        "x": player["x"], "y": player["y"],
                        "angle": math.radians(player["angle"]),
                        "dmg": player["weapon_dmg"],
                        "life": 90,
                        "source": "player"
                    })
                if event.key == pygame.K_e:
                    scan_rom()
                if event.key == pygame.K_m:
                    mine()
            if state == STATE_GALAXY_MAP:
                if event.key == pygame.K_r:
                    # Random warp
                    if uni.zones:
                        current_zone = random.choice(uni.zones)
                        current_galaxy = next((g for g in uni.galaxies if g["name"] == current_zone.get("galaxy")), None)
                        player["x"], player["y"] = 0, 0
                        player["vx"] = player["vy"] = 0
                        state = STATE_ZONE
                        spawn_enemies(current_zone)
                        set_message(f"Warped to {current_zone.get('name', 'Unknown')}!")

        if event.type == pygame.MOUSEBUTTONDOWN and state == STATE_GALAXY_MAP:
            mx, my = event.pos
            for g in uni.galaxies:
                if math.hypot(mx - g["x"], my - g["y"]) < 30:
                    current_galaxy = g
                    # Pick a zone in this galaxy
                    galaxy_zones = [z for z in uni.zones if z.get("galaxy") == g["name"]]
                    if galaxy_zones:
                        current_zone = random.choice(galaxy_zones)
                    else:
                        current_zone = random.choice(uni.zones)
                    player["x"], player["y"] = 0, 0
                    player["vx"] = player["vy"] = 0
                    state = STATE_ZONE
                    spawn_enemies(current_zone)
                    set_message(f"Entering {g['name'].replace('_', ' ')}...")
                    break

    if state == STATE_GALAXY_MAP:
        draw_galaxy_map()
    elif state == STATE_ZONE:
        update_zone(dt)
        draw_zone()
    elif state == STATE_BASE:
        draw_base_menu()

    draw_message()
    pygame.display.flip()

pygame.quit()
print("Project Nexus exited. Save preserved.")
