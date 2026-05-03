# Project Nexus: Space Universe — 3D Game

A third-person 3D action game built with **Ursina Engine** (Python). Explore procedurally-generated galaxies, build bases across 362 ROM worlds, fight enemies, complete quests, trade resources, and summon vehicles.

## Files

- `nexus_3d.py` — Main game loop, player, camera, HUD, day/night cycle
- `world_generator.py` — Procedural terrain, cities, POIs, quest givers, shops, vehicles
- `enemy_system.py` — Enemy AI with day/night sleep behavior
- `universe.py` — Loads 362-ROM database, galaxy/zone data, companion data

## Requirements

```bash
pip install -r requirements.txt
```

> **Standalone:** All game data (ROM database, galaxies, zones, companions, textures) is now bundled inside the `Game3D/` folder. You can move or copy the entire `Game3D` directory anywhere and it will run independently.

## Running the Game

### Windows

```batch
play.bat
```

Or manually:
```batch
pip install -r requirements.txt
python nexus_3d.py
```

### Linux / macOS

```bash
./play.sh
```

Or manually:
```bash
pip install -r requirements.txt
python3 nexus_3d.py
```

## Building a Standalone Executable

You can turn the game into a single distributable folder (no Python required on the player's machine).

**On either Windows or Linux, run:**

```bash
python build.py
```

This will:
1. Create a local build virtual environment
2. Install dependencies + PyInstaller
3. Bundle the game, data, and textures into `dist/ProjectNexus/`

**Linux output:** `dist/ProjectNexus/ProjectNexus` (~100 MB)  
**Windows output:** `dist/ProjectNexus/ProjectNexus.exe` (~100 MB)

> **Note:** PyInstaller builds are platform-specific. Build on Linux for Linux players, build on Windows for Windows players. To build for Windows from Linux, use Wine or a Windows VM.

Zip the `dist/ProjectNexus/` folder and share it — players just double-click the executable.

## Controls

| Key | Action |
|-----|--------|
| **WASD** | Move |
| **Mouse** | Look / Aim |
| **Left Shift** | Run |
| **Space** | Jump |
| **Left Click** | Shoot |
| **Mouse Right** | Rotate Camera (hold) |
| **E** | Interact (talk / trade) |
| **V** | Summon Hoverbike |
| **Shift+V** | Summon Ship |
| **B** | Toggle Build Mode |
| **Tab** (in Build Mode) | Cycle building type |
| **Left Click** (in Build Mode) | Place structure |
| **M** | Mine minerals |
| **Q** | Show Quest Log |
| **F5** | Save game |
| **Esc** | Exit build/UI mode |

## Features

### 1. Quest System
- **Quest Giver NPCs** spawn in every **neutral city** (golden-colored cube NPCs).
- Press **E** near them to receive fetch/kill/scan quests.
- Active quests are tracked in the Quest Log (**Q** key).
- Kill enemies or collect items to progress; rewards are auto-claimed on completion.

### 2. Trading & Economy
- **Shops** exist in neutral cities (blue cube buildings).
- Press **E** near a shop to buy health packs, armor, upgrades.
- Hold **Shift+E** to sell items (demo: sells health pack).
- Credits are earned from ROM scans, mining, quests, and selling.

### 3. Vehicle Summoning
- Press **V** to summon a **hoverbike** at your location — mounts automatically.
- Press **Shift+V** to summon a **spaceship** (faster).
- Vehicles follow your camera direction; dismount by summoning a different vehicle or moving far away.

### 4. Day/Night Cycle
- Full 24-hour cycle (~5 min real-time per day).
- Sun moves, sky color shifts from blue day to starry night.
- **Enemies sleep at night** (20:00–04:00): they return to spawn and stop attacking.
- Safe to explore enemy zones at night (except bosses guarding outposts).

### 5. N64 Terrain Textures
- Terrain uses **Hyrule Field floor textures** extracted from the OOT mod pack.
- Found in `textures/hyrule_floor*.png`.
- Fallback to Ursina `grass` texture if files missing.

### 6. Base Building
- Press **B** to enter build mode.
- **Tab** cycles through: Wall, Tower, Turret, Generator, Landing Pad.
- Structures cost credits and persist in your save.

### 7. ROM Discovery
- Press **E** to scan a random ROM sector from the 362-world database.
- First-time scans reward **XP + Credits**.
- Discover all 362 ROMs to complete the collector challenge.

### 8. Mining
- Press **M** to mine nearby minerals.
- Upgrade mineral yield at the shop (`mining_drill` item).

## Save Data

Saved to `save.json` inside the `Game3D/` folder:
- Player stats (HP, level, credits, XP, minerals)
- Position
- Base structures built
- Discovered ROM IDs
- Active Pokemon companion (placeholder)

## Architecture Overview

- **Player** (`nexus_3d.py`): Movement, jumping, shooting, save/load, vehicle control
- **Camera** (`ThirdPersonCamera`): Orbit camera with mouse drag (right button)
- **HUD**: On-screen stats, messages, quest log (Q), build mode overlay
- **World** (`world_generator.py`): Chunked procedural terrain, city/POI generation
- **City**: Contains `Building` entities, `QuestGiver` NPCs, `Shop` vendors
- **QuestGiver**: Generates random fetch/kill/scan quests; tracks completion
- **Shop**: Buy/sell items that buff player stats
- **Vehicle**: Mountable hoverbike/ship that player can summon (V key)
- **EnemyManager** (`enemy_system.py`): Spawns and updates enemies; respects day/night sleep
- **Enemy**: State machine (patrol/chase/attack); HP bar, projectile attack

## Extensibility

Each system is self-contained:
- Add new quest types by expanding `QuestGiver._generate_quests()`
- Add new shop items by extending `Shop.inventory`
- Add new vehicle types by adding a `Vehicle` variant
- Terrain chunk resolution/scale tuned in `TerrainChunk.__init__`
- Day length adjustable via `DayNightCycle.day_length`

## Troubleshooting

**Textures not loading:** Ensure `textures/` directory contains `hyrule_floor.png`. If missing, the game falls back to Ursina's built-in `grass` texture.

**ModuleNotFoundError:** Install dependencies: `pip install ursina noise`

**Save file corrupted:** Delete `save.json` to reset.

## Credits

Built with Ursina Engine. N64 textures sourced from the OOT AI Reloaded mod pack. ROM universe data from the Ship of Harkinian AI Full Universe mod.
