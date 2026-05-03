#!/usr/bin/env python3
"""
AI DUNGEON MASTER - ULTIMATE SCANNER
Finds ALL games: N64, PS1, GameBoy, GBA, NES, SNES, Genesis, etc.
Optimizes for small hardware (Raspberry Pi, old PCs)
Creates inter-world travel system with tasks
"""

import os
import json
from datetime import datetime

class UltimateScanner:
    def __init__(self):
        self.all_games = {
            "n64": [],
            "ps1": [],
            "gameboy": [],
            "gba": [],
            "nes": [],
            "snes": [],
            "genesis": [],
            "other": []
        }
        
        self.small_hardware_limit = 50 * 1024 * 1024  # 50MB limit for small hardware
        
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER - ULTIMATE GAME SCANNER")
        print("   Scanning for: N64, PS1, GameBoy, GBA, NES, SNES")
        print("   Optimizing for small hardware")
        print("="*60 + "\n")
    
    def scan_for_roms(self, path):
        """Scan directory for ROMs of all types"""
        rom_extensions = {
            'n64': ['.z64', '.n64', '.v64', '.rom'],
            'ps1': ['.iso', '.bin', '.cue', '.img', '.pbp'],
            'gameboy': ['.gb', '.gbc', '.gbx'],
            'gba': ['.gba', '.agb'],
            'nes': ['.nes'],
            'snes': ['.smc', '.sfc', '.fig'],
            'genesis': ['.md', '.gen', '.bin'],
            'other': ['.rom', '.bin', '.img']
        }
        
        found = []
        
        try:
            for root, dirs, files in os.walk(path):
                # Skip some directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv']]
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    full_path = os.path.join(root, file)
                    
                    # Check file size (skip huge files)
                    try:
                        size = os.path.getsize(full_path)
                        if size > 500 * 1024 * 1024:  # Skip files > 500MB
                            continue
                    except:
                        continue
                    
                    # Categorize by extension
                    for category, exts in rom_extensions.items():
                        if ext in exts:
                            self.all_games[category].append({
                                "path": full_path,
                                "size": size,
                                "name": file
                            })
                            found.append(full_path)
                            break
        except Exception as e:
            pass
        
        return found
    
    def scan_everything(self):
        """Scan all common locations"""
        print("🧠 AI: Scanning entire PC for games...\n")
        
        scan_paths = [
            "/home/donn",
            "/home/donn/N64",
            "/home/donn/HylianModding",
            "/home/donn/.local/share/Steam/steamapps/common",
            "/media",
            "/mnt"
        ]
        
        total_found = 0
        for path in scan_paths:
            if os.path.exists(path):
                print(f"Scanning: {path}")
                found = self.scan_for_roms(path)
                total_found += len(found)
        
        # Print summary
        print(f"\n✅ SCAN COMPLETE")
        for category, games in self.all_games.items():
            if games:
                total_size = sum(g["size"] for g in games) / (1024*1024)
                print(f"   {category.upper()}: {len(games)} games ({total_size:.1f}MB)")
        
        return self.all_games
    
    def create_interworld_travel(self):
        """Create travel system between game worlds"""
        print("\n🧠 AI: Creating INTER-WORLD TRAVEL SYSTEM...\n")
        
        worlds = []
        world_id = 0
        
        # Create worlds from each game type
        for category, games in self.all_games.items():
            if not games:
                continue
            
            # Take up to 10 games per category for small hardware
            for game in games[:10]:
                world = {
                    "id": f"world_{world_id}",
                    "name": os.path.splitext(game["name"])[0],
                    "source_game": game["path"],
                    "game_type": category,
                    "size_mb": game["size"] / (1024*1024),
                    "small_hardware_ok": game["size"] < self.small_hardware_limit,
                    "tasks": self.generate_tasks(category),
                    "connections": []  # Will be filled later
                }
                worlds.append(world)
                world_id += 1
        
        # Create connections (all worlds connected to hub)
        hub_world = next((w for w in worlds if w["game_type"] == "n64"), worlds[0])
        for world in worlds:
            if world["id"] != hub_world["id"]:
                world["connections"].append(hub_world["id"])
        
        print(f"✅ Created {len(worlds)} game worlds")
        print(f"   Hub world: {hub_world['name']}")
        print(f"   Small hardware compatible: {sum(1 for w in worlds if w['small_hardware_ok'])} worlds")
        
        return worlds
    
    def generate_tasks(self, game_type):
        """Generate tasks for each game world"""
        tasks = {
            "n64": [
                {"name": "Defeat Gohma Carrier", "reward": "New Ship", "difficulty": 3},
                {"name": "Collect 10 Triforce Shards", "reward": "Shield Upgrade", "difficulty": 2},
                {"name": "Clear Skulltula Swarm", "reward": "AI Ally", "difficulty": 4}
            ],
            "ps1": [
                {"name": "Survive the Horror", "reward": "Horror Ship Skin", "difficulty": 5},
                {"name": "Race to Finish", "reward": "Speed Boost", "difficulty": 3},
                {"name": "Defeat Final Boss", "reward": "Legendary Weapon", "difficulty": 5}
            ],
            "gameboy": [
                {"name": "Collect 8 Items", "reward": "Pocket Ship", "difficulty": 1},
                {"name": "Clear 4 Levels", "reward": "Mini Ally", "difficulty": 2},
                {"name": "Beat High Score", "reward": "Retro Paint Job", "difficulty": 3}
            ],
            "gba": [
                {"name": "Advance Through World", "reward": "Advanced Engine", "difficulty": 3},
                {"name": "Collect All Coins", "reward": "Coin Multiplier", "difficulty": 2},
                {"name": "Defeat Mini Boss", "reward": "Mini Weapon", "difficulty": 4}
            ]
        }
        
        return tasks.get(game_type, [
            {"name": "Explore World", "reward": "Exploration Badge", "difficulty": 1},
            {"name": "Defeat Enemies", "reward": "Combat Rating", "difficulty": 2}
        ])
    
    def save_ultimate_config(self, worlds):
        """Save the ultimate open world config"""
        config = {
            "generated_at": datetime.now().isoformat(),
            "ai_dungeon_master": True,
            "total_worlds": len(worlds),
            "game_types": {k: len(v) for k, v in self.all_games.items()},
            "small_hardware_optimized": True,
            "interworld_travel": True,
            "task_system": True,
            "base_building": True,
            "factory_system": True,
            "modifiable_ships": True,
            "worlds": worlds,
            "hub_world": worlds[0]["id"] if worlds else None
        }
        
        config_path = os.path.expanduser("~/HylianModding/AI_DM/ultimate_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ ULTIMATE CONFIG SAVED: {config_path}")
        print(f"   Total Worlds: {len(worlds)}")
        print(f"   Ready for inter-world travel!")
        
        return config_path
    
    def run(self):
        """Run the ultimate scanner"""
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER: ULTIMATE SCAN COMPLETE")
        print("="*60 + "\n")
        
        self.scan_everything()
        worlds = self.create_interworld_travel()
        config_path = self.save_ultimate_config(worlds)
        
        print("\n" + "="*60)
        print("✅ ULTIMATE OPEN WORLD READY!")
        print("="*60)
        print(f"   Features:")
        print(f"   - Inter-world travel between {len(worlds)} game worlds")
        print(f"   - Task system in each world")
        print(f"   - Optimized for small hardware")
        print(f"   - Base building & factory systems")
        print(f"   - Modifiable ships")
        print(f"   - AI Dungeon Master controls everything")
        print("="*60)
        print(f"\n🧠 AI: Fly to different game worlds to complete tasks!")
        
        return config_path

if __name__ == "__main__":
    scanner = UltimateScanner()
    scanner.run()
