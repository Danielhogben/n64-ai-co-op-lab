#!/usr/bin/env python3
"""
AI Dungeon Master - Controls the entire game world
Generates random events, modifies content, scales difficulty
Run this to have the AI take control of the game
"""

import json
import random
import os
from datetime import datetime

class AIDungeonMaster:
    def __init__(self):
        self.game_state = {
            "player_health": 100,
            "score": 0,
            "level": 1,
            "enemies_defeated": 0,
            "current_area": "Hyrule Space Station",
            "difficulty": 1,
            "random_events_active": True,
            "ai_controlled": True
        }
        self.event_types = [
            "enemy_swarm", "boss_rush", "speed_boost", "weapon_upgrade",
            "gravity_shift", "time_warp", "meteor_shower", "ally_reinforcements",
            "black_hole_spawn", "portal_storm"
        ]
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER ACTIVATED")
        print("   Powered by: big-pickle (opencode/big-pickle)")
        print("="*60 + "\n")
    
    def generate_random_event(self):
        """AI generates random events to keep gameplay dynamic"""
        event = random.choice(self.event_types)
        
        events = {
            "enemy_swarm": {
                "message": "⚠️ WARNING: Massive Skulltula swarm detected!",
                "effect": {"spawn_multiplier": 3, "dialogue": "The swarm is overwhelming!"},
                "duration": 30
            },
            "boss_rush": {
                "message": "💀 BOSS RUSH: Gohma Carrier approaching!",
                "effect": {"boss_health_multiplier": 1.5, "dialogue": "Prepare for the ultimate challenge!"},
                "duration": 60
            },
            "speed_boost": {
                "message": "⚡ ZELDA'S SPEED: Time flows faster!",
                "effect": {"player_speed": 2.0, "dialogue": "Feel the power of the Golden Goddesses!"},
                "duration": 15
            },
            "weapon_upgrade": {
                "message": "🔫 ARMORY UPGRADE: Triple laser unlocked!",
                "effect": {"weapon_type": "triple_laser", "dialogue": "New technology from Sheikah labs!"},
                "duration": 45
            },
            "gravity_shift": {
                "message": "🌌 GRAVITY FLUX: Physics altered!",
                "effect": {"gravity": 0.5, "dialogue": "The space-time continuum is unstable!"},
                "duration": 20
            },
            "time_warp": {
                "message": "⏳ TIME WARP: Bullet time engaged!",
                "effect": {"time_scale": 0.3, "dialogue": "The Song of Time echoes through space!"},
                "duration": 10
            },
            "meteor_shower": {
                "message": "☄️ METEOR SHOWER: Incoming debris!",
                "effect": {"hazards": True, "dialogue": "The heavens themselves attack!"},
                "duration": 40
            },
            "ally_reinforcements": {
                "message": "🤝 REINFORCEMENTS: AI ally joins the battle!",
                "effect": {"ally_damage": 15, "dialogue": "You are not alone in this fight!"},
                "duration": 50
            },
            "black_hole_spawn": {
                "message": "🕳️ BLACK HOLE: Gravity well detected!",
                "effect": {"black_hole": True, "dialogue": "A rift in space has opened!"},
                "duration": 35
            },
            "portal_storm": {
                "message": "🌀 PORTAL STORM: Dimensional rifts appear!",
                "effect": {"portals": True, "dialogue": "The veil between worlds thins!"},
                "duration": 25
            }
        }
        
        return event, events[event]
    
    def modify_game_world(self):
        """AI dynamically modifies the game world based on player progress"""
        self.game_state["enemies_defeated"] += random.randint(1, 5)
        self.game_state["score"] += random.randint(100, 1000)
        
        # Scale difficulty based on progress
        if self.game_state["enemies_defeated"] > 50:
            self.game_state["difficulty"] = 3
        elif self.game_state["enemies_defeated"] > 20:
            self.game_state["difficulty"] = 2
        
        # Randomly change area
        if random.random() < 0.3:
            areas = ["Hyrule Space Station", "Zora Nebula", "Ganon's Death Star", "Shadow Dimension"]
            self.game_state["current_area"] = random.choice(areas)
        
        return self.game_state
    
    def generate_ai_content(self):
        """AI generates new content on the fly"""
        content_types = ["enemy_variant", "powerup", "hazard", "boss_phase"]
        new_content = random.choice(content_types)
        
        generated = {
            "enemy_variant": {
                "name": f"AI_Skulltula_{random.randint(100,999)}",
                "health": random.randint(20, 50),
                "speed": random.choice(["erratic", "teleporting", "splitting"]),
                "ai_controlled": True
            },
            "powerup": {
                "name": random.choice(["Triforce Shard", "Sheikah Tech", "Fairy Spirit"]),
                "effect": random.choice(["invincibility", "rapid_fire", "homing_missiles"]),
                "duration": random.randint(10, 30)
            },
            "hazard": {
                "type": random.choice(["laser_grid", "pulse_wave", "nuclear_sun"]),
                "damage": random.randint(10, 40),
                "ai_generated": True
            },
            "boss_phase": {
                "phase": random.randint(2, 5),
                "attack_pattern": random.choice(["spiral", "cross", "circle_burst"]),
                "ai_designed": True
            }
        }
        
        return new_content, generated[new_content]
    
    def run_dm_session(self):
        """Main DM loop - AI controls everything"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] DM: Initializing game world...\n")
        
        for turn in range(1, 6):
            print(f"\n--- DM TURN {turn} ---")
            
            # Modify world
            state = self.modify_game_world()
            print(f"DM: Player in {state['current_area']}")
            print(f"DM: Difficulty Level {state['difficulty']} | Score: {state['score']}")
            
            # Generate random event
            event_name, event_data = self.generate_random_event()
            print(f"\n🎲 RANDOM EVENT: {event_data['message']}")
            print(f"   Effect: {event_data['effect']['dialogue']}")
            
            # Generate new content
            content_type, content = self.generate_ai_content()
            print(f"\n🧠 AI GENERATED: {content_type.upper()}")
            print(f"   {json.dumps(content, indent=8)}")
            
            print(f"\n{'-'*40}")
        
        print(f"\n{'='*60}")
        print("🧠 DM SESSION COMPLETE - AI CONTROL ACTIVE")
        print(f"Final State: {json.dumps(self.game_state, indent=2)}")
        print(f"{'='*60}")
        
        # Save DM state for game to use
        with open('dm_game_state.json', 'w') as f:
            json.dump({
                "game_state": self.game_state,
                "last_update": datetime.now().isoformat(),
                "ai_controller": "big-pickle",
                "dm_active": True
            }, f, indent=2)
        
        print("\n✅ Game state saved to dm_game_state.json")
        print("   The AI Dungeon Master is now controlling the game world!")

if __name__ == "__main__":
    dm = AIDungeonMaster()
    dm.run_dm_session()
