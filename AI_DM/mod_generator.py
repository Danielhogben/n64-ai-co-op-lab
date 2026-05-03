#!/usr/bin/env python3
"""
AI DUNGEON MASTER - MOD GENERATOR
Generates actual SoH-compatible mods with random content
The AI creates: scenes, actors, textures, and gameplay modifications
"""

import json
import random
import os
import shutil
from datetime import datetime

class AIModGenerator:
    def __init__(self):
        self.mod_id = f"ai_dm_mod_{random.randint(1000, 9999)}"
        self.base_path = os.path.expanduser(f"~/HylianModding/ShipOfHarkinian/mods/{self.mod_id}")
        self.assets_path = os.path.join(self.base_path, "assets")
        self.scenes_path = os.path.join(self.base_path, "scenes")
        self.actors_path = os.path.join(self.base_path, "actors")
        
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER - MOD GENERATOR")
        print(f"   Mod ID: {self.mod_id}")
        print(f"   Base: {self.base_path}")
        print("="*60 + "\n")
    
    def create_mod_structure(self):
        """Create the mod directory structure"""
        os.makedirs(self.assets_path, exist_ok=True)
        os.makedirs(self.scenes_path, exist_ok=True)
        os.makedirs(self.actors_path, exist_ok=True)
        print(f"✅ Created mod structure at {self.base_path}")
    
    def generate_random_scene(self):
        """AI generates a random scene/level"""
        scene_types = ["space_station", "nebula_field", "death_star", "asteroid_belt", "black_hole"]
        scene_name = random.choice(scene_types)
        scene_id = f"scene_{random.randint(100, 999)}"
        
        scene = {
            "id": scene_id,
            "name": f"AI_{scene_name}_{random.randint(10, 99)}",
            "type": scene_name,
            "difficulty": random.randint(1, 10),
            "enemies": random.randint(5, 30),
            "boss": random.choice([True, False]),
            "ai_generated": True,
            "theme": random.choice(["dark", "neon", "retro", "glitch"]),
            "music": random.choice(["battle", "ambient", "boss", "victory"]),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save scene file
        scene_file = os.path.join(self.scenes_path, f"{scene_id}.json")
        with open(scene_file, 'w') as f:
            json.dump(scene, f, indent=2)
        
        print(f"🎲 GENERATED SCENE: {scene['name']} (Difficulty: {scene['difficulty']})")
        return scene
    
    def generate_random_actor(self):
        """AI generates a random actor/enemy"""
        actor_types = ["enemy", "npc", "boss", "hazard", "powerup"]
        actor_name = random.choice(["Skulltula", "DarkLink", "Gohma", "Zelda", "Ganon", "AI_Spawn"])
        
        actor = {
            "id": f"actor_{random.randint(1000, 9999)}",
            "name": f"AI_{actor_name}_{random.randint(10, 99)}",
            "type": random.choice(actor_types),
            "health": random.randint(10, 500),
            "damage": random.randint(5, 100),
            "speed": random.choice(["slow", "normal", "fast", "teleporting"]),
            "behavior": random.choice(["passive", "aggressive", "cowardly", "berserk", "random"]),
            "ai_controlled": True,
            "model": f"{actor_name.lower()}_model.obj",
            "texture": f"{actor_name.lower()}_tex.png",
            "generated_at": datetime.now().isoformat()
        }
        
        # Save actor file
        actor_file = os.path.join(self.actors_path, f"{actor['id']}.json")
        with open(actor_file, 'w') as f:
            json.dump(actor, f, indent=2)
        
        print(f"🎲 GENERATED ACTOR: {actor['name']} (HP:{actor['health']} DMG:{actor['damage']})")
        return actor
    
    def generate_mod_manifest(self, scenes, actors):
        """Generate the mod manifest that SoH reads"""
        manifest = {
            "id": self.mod_id,
            "name": f"AI DM Mod {self.mod_id}",
            "author": "big-pickle (opencode/big-pickle)",
            "version": "1.0.0",
            "description": "AI Dungeon Master generated mod with random content",
            "type": "gameplay",
            "ai_generated": True,
            "generated_at": datetime.now().isoformat(),
            "scenes": [s["id"] for s in scenes],
            "actors": [a["id"] for a in actors],
            "random_seed": random.randint(1000, 9999),
            "difficulty": random.randint(1, 10),
            "tags": ["ai", "random", "dm_controlled", "space_shooter"]
        }
        
        manifest_file = os.path.join(self.base_path, "manifest.json")
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Generated mod manifest: {manifest_file}")
        return manifest
    
    def generate_mod(self):
        """Generate a complete mod with random content"""
        print("\n🧠 AI DM: Generating random mod content...\n")
        
        self.create_mod_structure()
        
        # Generate random scenes (3-8)
        scenes = []
        for _ in range(random.randint(3, 8)):
            scenes.append(self.generate_random_scene())
        
        # Generate random actors (5-15)
        actors = []
        for _ in range(random.randint(5, 15)):
            actors.append(self.generate_random_actor())
        
        # Generate manifest
        manifest = self.generate_mod_manifest(scenes, actors)
        
        print(f"\n✅ MOD GENERATION COMPLETE")
        print(f"   Scenes: {len(scenes)}")
        print(f"   Actors: {len(actors)}")
        print(f"   Mod ID: {self.mod_id}")
        print(f"   Location: {self.base_path}")
        
        return manifest

if __name__ == "__main__":
    generator = AIModGenerator()
    generator.generate_mod()
