"""Procedural dungeon generator with rooms, corridors, and treasure."""
import random
from ursina import *

class DungeonGenerator:
    def __init__(self, size=8, room_count=6):
        self.size = size
        self.room_count = room_count
        self.grid = [[1 for _ in range(size)] for _ in range(size)]
        self.rooms = []
        self.generate()

    def generate(self):
        # Place rooms
        for _ in range(self.room_count):
            x = random.randint(1, self.size - 3)
            z = random.randint(1, self.size - 3)
            w = random.randint(2, 3)
            h = random.randint(2, 3)
            for rx in range(x, min(x + w, self.size - 1)):
                for rz in range(z, min(z + h, self.size - 1)):
                    self.grid[rz][rx] = 0
            self.rooms.append((x, z, w, h))

        # Connect rooms with corridors
        for i in range(len(self.rooms) - 1):
            x1, z1, _, _ = self.rooms[i]
            x2, z2, _, _ = self.rooms[i + 1]
            cx, cz = x1 + 1, z1 + 1
            while cx != x2 + 1:
                self.grid[cz][cx] = 0
                cx += 1 if cx < x2 + 1 else -1
            while cz != z2 + 1:
                self.grid[cz][cx] = 0
                cz += 1 if cz < z2 + 1 else -1

    def build_3d(self, world_offset=Vec3(0, -20, 0), tile_size=4):
        entities = []
        for z in range(self.size):
            for x in range(self.size):
                pos = world_offset + Vec3(x * tile_size, 0, z * tile_size)
                if self.grid[z][x] == 1:
                    # Wall
                    wall = Entity(model='cube', color=color.gray, position=pos + Vec3(0, 2, 0), scale=(tile_size, 4, tile_size), collider='box')
                    entities.append(wall)
                else:
                    # Floor
                    floor = Entity(model='cube', color=color.dark_gray, position=pos, scale=(tile_size, 0.2, tile_size))
                    entities.append(floor)
                    # Ceiling
                    ceil = Entity(model='cube', color=color.black, position=pos + Vec3(0, 4, 0), scale=(tile_size, 0.2, tile_size))
                    entities.append(ceil)

        # Entrance portal
        if self.rooms:
            rx, rz, _, _ = self.rooms[0]
            portal = Entity(model='sphere', color=color.cyan, scale=1.5, position=world_offset + Vec3(rx * tile_size, 2, rz * tile_size))
            entities.append(portal)

        # Exit portal
        if len(self.rooms) > 1:
            rx, rz, _, _ = self.rooms[-1]
            exit_p = Entity(model='sphere', color=color.red, scale=1.5, position=world_offset + Vec3(rx * tile_size, 2, rz * tile_size))
            entities.append(exit_p)

        # Treasure chests in random rooms
        for room in random.sample(self.rooms, min(3, len(self.rooms))):
            rx, rz, rw, rh = room
            cx = rx + rw // 2
            cz = rz + rh // 2
            chest = Entity(model='cube', color=color.gold, scale=0.8, position=world_offset + Vec3(cx * tile_size, 1, cz * tile_size))
            entities.append(chest)

        return entities


class DungeonManager:
    def __init__(self):
        self.active = False
        self.entities = []
        self.entrance_pos = None

    def enter(self, player):
        if self.active:
            return
        self.active = True
        self.entrance_pos = Vec3(player.position)
        gen = DungeonGenerator(size=10, room_count=8)
        self.entities = gen.build_3d(world_offset=Vec3(0, -30, 0), tile_size=5)
        player.position = Vec3(0, -28, 0)

    def exit(self, player):
        if not self.active:
            return
        self.active = False
        for e in self.entities:
            destroy(e)
        self.entities = []
        if self.entrance_pos:
            player.position = self.entrance_pos
