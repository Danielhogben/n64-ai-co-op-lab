#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Procedural Level Generator
==============================================
Generates N64-compatible level layouts as JSON/CSV, which can be
imported into Blender via Fast64 or SharpOcarina.
"""

import os
import json
import random
import numpy as np

OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/generated_levels")

# N64 constraints
MAX_VERTS_PER_ROOM = 800
MAX_TRIS_PER_ROOM = 1200
ROOM_SIZE = 20.0

TILE_TYPES = {
    "empty": {"walkable": True, "height": 0},
    "floor": {"walkable": True, "height": 0},
    "wall": {"walkable": False, "height": 3},
    "door": {"walkable": True, "height": 0, "locked": True},
    "pit": {"walkable": False, "height": -5},
    "water": {"walkable": False, "height": -1},
    "lava": {"walkable": False, "height": -1, "damage": 10},
    "chest": {"walkable": True, "height": 0, "loot": True},
    "switch": {"walkable": True, "height": 0, "interact": True},
    "enemy_spawn": {"walkable": True, "height": 0, "enemy": True},
    "boss_spawn": {"walkable": True, "height": 0, "boss": True},
    "start": {"walkable": True, "height": 0, "spawn": True},
    "exit": {"walkable": True, "height": 0, "exit": True},
}


def generate_dungeon_grid(width=16, height=16, theme="dungeon", difficulty=3):
    """Generate a 2D tile grid representing a dungeon room/level."""
    grid = [["wall" for _ in range(width)] for _ in range(height)]
    
    # Room carving using recursive backtracker-ish approach
    rooms = []
    num_rooms = 3 + difficulty
    
    for _ in range(num_rooms * 10):  # Attempts
        if len(rooms) >= num_rooms:
            break
        rw = random.randint(3, 6)
        rh = random.randint(3, 6)
        rx = random.randint(1, width - rw - 1)
        ry = random.randint(1, height - rh - 1)
        
        # Check overlap
        overlap = False
        for r in rooms:
            if (rx < r["x"] + r["w"] and rx + rw > r["x"] and
                ry < r["y"] + r["h"] and ry + rh > r["y"]):
                overlap = True
                break
        
        if not overlap:
            rooms.append({"x": rx, "y": ry, "w": rw, "h": rh})
            for y in range(ry, ry + rh):
                for x in range(rx, rx + rw):
                    grid[y][x] = "floor"
    
    # Connect rooms with corridors
    for i in range(len(rooms) - 1):
        r1 = rooms[i]
        r2 = rooms[i + 1]
        c1 = (r1["x"] + r1["w"] // 2, r1["y"] + r1["h"] // 2)
        c2 = (r2["x"] + r2["w"] // 2, r2["y"] + r2["h"] // 2)
        
        # L-shaped corridor
        cx, cy = c1
        while cx != c2[0]:
            grid[cy][cx] = "floor"
            cx += 1 if c2[0] > cx else -1
        while cy != c2[1]:
            grid[cy][cx] = "floor"
            cy += 1 if c2[1] > cy else -1
    
    # Place special tiles
    if rooms:
        start_room = rooms[0]
        sx = start_room["x"] + start_room["w"] // 2
        sy = start_room["y"] + start_room["h"] // 2
        grid[sy][sx] = "start"
        
        end_room = rooms[-1]
        ex = end_room["x"] + end_room["w"] // 2
        ey = end_room["y"] + end_room["h"] // 2
        grid[ey][ex] = "exit"
    
    # Place enemies and chests
    enemy_count = difficulty * 2
    chest_count = 1 + difficulty // 2
    
    floor_tiles = [(x, y) for y in range(height) for x in range(width) if grid[y][x] == "floor"]
    random.shuffle(floor_tiles)
    
    for i in range(min(enemy_count, len(floor_tiles))):
        x, y = floor_tiles[i]
        grid[y][x] = "enemy_spawn"
    
    for i in range(enemy_count, min(enemy_count + chest_count, len(floor_tiles))):
        x, y = floor_tiles[i]
        grid[y][x] = "chest"
    
    # Theme-specific modifications
    if theme == "ice":
        for y in range(height):
            for x in range(width):
                if grid[y][x] == "floor" and random.random() < 0.1:
                    grid[y][x] = "water"
    elif theme == "fire":
        for y in range(height):
            for x in range(width):
                if grid[y][x] == "floor" and random.random() < 0.08:
                    grid[y][x] = "lava"
    elif theme == "shadow":
        # More enemies, fewer chests
        pass
    
    return {
        "width": width,
        "height": height,
        "theme": theme,
        "difficulty": difficulty,
        "grid": grid,
        "rooms": rooms,
    }


def grid_to_3d_mesh(level):
    """Convert tile grid to simple 3D mesh data (vertices + faces)."""
    verts = []
    faces = []
    tile_size = 2.0
    
    vert_idx = {}
    def get_vert(x, y, z):
        key = (round(x, 3), round(y, 3), round(z, 3))
        if key not in vert_idx:
            vert_idx[key] = len(verts)
            verts.append([x, y, z])
        return vert_idx[key]
    
    for y, row in enumerate(level["grid"]):
        for x, tile in enumerate(row):
            if tile == "empty":
                continue
            
            info = TILE_TYPES.get(tile, TILE_TYPES["floor"])
            h = info.get("height", 0)
            
            # Create a box for this tile
            x0, x1 = x * tile_size, (x + 1) * tile_size
            z0, z1 = y * tile_size, (y + 1) * tile_size
            y0, y1 = 0, h * tile_size * 0.5
            
            if tile == "pit":
                y1 = -tile_size
            
            v = [
                get_vert(x0, y0, z0), get_vert(x1, y0, z0),
                get_vert(x1, y0, z1), get_vert(x0, y0, z1),
                get_vert(x0, y1, z0), get_vert(x1, y1, z0),
                get_vert(x1, y1, z1), get_vert(x0, y1, z1),
            ]
            
            # Bottom
            faces.append([v[0], v[1], v[2], v[3]])
            # Top
            faces.append([v[4], v[7], v[6], v[5]])
            # Sides
            faces.append([v[0], v[4], v[5], v[1]])
            faces.append([v[1], v[5], v[6], v[2]])
            faces.append([v[2], v[6], v[7], v[3]])
            faces.append([v[3], v[7], v[4], v[0]])
    
    return {"vertices": verts, "faces": faces, "name": f"{level['theme']}_level"}


def export_level_json(level, name=None):
    """Save level as JSON for game engine consumption."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not name:
        name = f"{level['theme']}_diff{level['difficulty']}"
    
    path = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(level, f, indent=2)
    
    # Also export 3D mesh
    mesh = grid_to_3d_mesh(level)
    mesh_path = os.path.join(OUTPUT_DIR, f"{name}_mesh.json")
    with open(mesh_path, "w") as f:
        json.dump(mesh, f, indent=2)
    
    print(f"[LevelGen] Saved level to {path} ({len(mesh['vertices'])} verts)")
    return path


def generate_full_dungeon(theme="dungeon", difficulty=3, num_rooms=3):
    """Generate a multi-room dungeon with connecting corridors."""
    dungeon = {
        "theme": theme,
        "difficulty": difficulty,
        "rooms": [],
    }
    
    for i in range(num_rooms):
        room = generate_dungeon_grid(
            width=12 + random.randint(0, 8),
            height=12 + random.randint(0, 8),
            theme=theme,
            difficulty=difficulty,
        )
        room["id"] = f"room_{i}"
        dungeon["rooms"].append(room)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{theme}_dungeon_diff{difficulty}.json")
    with open(path, "w") as f:
        json.dump(dungeon, f, indent=2)
    
    print(f"[LevelGen] Generated {num_rooms}-room dungeon: {path}")
    return dungeon


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default="dungeon")
    parser.add_argument("--difficulty", type=int, default=3)
    parser.add_argument("--rooms", type=int, default=3)
    parser.add_argument("--single", action="store_true", help="Generate single room")
    args = parser.parse_args()
    
    if args.single:
        level = generate_dungeon_grid(theme=args.theme, difficulty=args.difficulty)
        export_level_json(level)
    else:
        generate_full_dungeon(args.theme, args.difficulty, args.rooms)
