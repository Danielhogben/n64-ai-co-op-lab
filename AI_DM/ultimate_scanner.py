#!/usr/bin/env python3
"""
AI DUNGEON MASTER - ULTIMATE SCANNER (N64 & 3DS Focus)
Finds ONLY N64 and 3DS games.
Optimizes for small hardware (Raspberry Pi, old PCs)
"""

import os
import json
from datetime import datetime
from rr_analyzer import RetroReversingAnalyzer

class UltimateScanner:
    def __init__(self):
        self.analyzer = RetroReversingAnalyzer()
        self.all_games = {
            "n64": [],
            "3ds": []
        }
        
        self.small_hardware_limit = 100 * 1024 * 1024  # 100MB limit for small hardware
        
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER - ULTIMATE GAME SCANNER")
        print("   Focusing on: N64 and 3DS")
        print("   Powered by RetroReversing Tools")
        print("="*60 + "\n")
    
    def scan_for_roms(self, path):
        """Scan directory for N64 and 3DS ROMs"""
        rom_extensions = {
            'n64': ['.z64', '.n64', '.v64', '.rom'],
            '3ds': ['.3ds', '.cia', '.app', '.cxi', '.cci']
        }
        
        found = []
        
        try:
            for root, dirs, files in os.walk(path):
                # Skip irrelevant directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', 'RetroReversing']]
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    full_path = os.path.join(root, file)
                    
                    # Check file size (skip huge files > 4GB)
                    try:
                        size = os.path.getsize(full_path)
                        if size > 4000 * 1024 * 1024:
                            continue
                    except:
                        continue
                    
                    # Categorize by extension
                    for category, exts in rom_extensions.items():
                        if ext in exts:
                            # Deep Analysis using RetroReversing tools (for N64)
                            metadata = self.analyzer.get_deep_metadata(category, full_path)
                            
                            self.all_games[category].append({
                                "path": full_path,
                                "size": size,
                                "name": file,
                                "metadata": metadata
                            })
                            found.append(full_path)
                            break
        except Exception as e:
            print(f"Error scanning {path}: {e}")
        
        return found
    
    def scan_everything(self):
        """Scan all common locations"""
        print("🧠 AI: Scanning for N64 and 3DS games...\n")
        
        scan_paths = [
            "/home/donn",
            "/home/donn/N64",
            "/home/donn/HylianModding",
            "/home/donn/Downloads"
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
        print("\n🧠 AI: Creating N64/3DS INTER-WORLD TRAVEL SYSTEM...\n")
        
        worlds = []
        world_id = 0
        
        # Create worlds
        for category, games in self.all_games.items():
            if not games:
                continue
            
            # Take up to 20 games per category
            for game in games[:20]:
                world = {
                    "id": f"world_{world_id}",
                    "name": os.path.splitext(game["name"])[0],
                    "source_game": game["path"],
                    "game_type": category,
                    "size_mb": game["size"] / (1024*1024),
                    "small_hardware_ok": game["size"] < self.small_hardware_limit,
                    "tasks": self.generate_tasks(category),
                    "connections": []
                }
                worlds.append(world)
                world_id += 1
        
        # Hub logic (prefer N64)
        if worlds:
            hub_world = next((w for w in worlds if w["game_type"] == "n64"), worlds[0])
            for world in worlds:
                if world["id"] != hub_world["id"]:
                    world["connections"].append(hub_world["id"])
        
        return worlds
    
    def generate_tasks(self, game_type):
        """Generate tasks for N64 or 3DS worlds"""
        if game_type == "n64":
            return [
                {"name": "Defeat Gohma Carrier", "reward": "New Ship", "difficulty": 3},
                {"name": "Collect 10 Triforce Shards", "reward": "Shield Upgrade", "difficulty": 2},
                {"name": "Clear Skulltula Swarm", "reward": "AI Ally", "difficulty": 4}
            ]
        elif game_type == "3ds":
            return [
                {"name": "Sync StreetPass Data", "reward": "Communication Array", "difficulty": 2},
                {"name": "Survive 3D Dimension Shift", "reward": "Dimensional Engine", "difficulty": 5},
                {"name": "Defeat Totem Boss", "reward": "Totem Weapon", "difficulty": 6}
            ]
        return []
    
    def save_ultimate_config(self, worlds):
        """Save the refined config"""
        config = {
            "generated_at": datetime.now().isoformat(),
            "ai_dungeon_master": True,
            "total_worlds": len(worlds),
            "game_types": {k: len(v) for k, v in self.all_games.items()},
            "worlds": worlds,
            "hub_world": worlds[0]["id"] if worlds else None
        }
        
        config_path = os.path.expanduser("~/HylianModding/AI_DM/ultimate_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ REFINED CONFIG SAVED: {config_path}")
        return config_path

    def run(self):
        self.scan_everything()
        worlds = self.create_interworld_travel()
        return self.save_ultimate_config(worlds)

if __name__ == "__main__":
    scanner = UltimateScanner()
    scanner.run()
