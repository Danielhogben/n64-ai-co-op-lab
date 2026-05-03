#!/usr/bin/env python3
"""
AI DUNGEON MASTER - FULL CONTROL MODE
Controls: enemies, events, world state, random generation
The AI decides EVERYTHING that happens in the game
"""

import json
import random
import time
import os
from datetime import datetime

class AIDungeonMaster:
    def __init__(self):
        self.tick = 0
        self.running = True
        self.game_state = {
            "player": {"health": 100, "score": 0, "x": 0, "y": 0, "weapon": "laser"},
            "world": {"time": 0, "difficulty": 1, "event_active": None, "area": "Hyrule Space Station"},
            "enemies": [],
            "active_events": [],
            "ai_personality": "chaotic_god",
            "random_seed": random.randint(1000, 9999)
        }
        
        print("\n" + "="*60)
        print("🧠 AI DUNGEON MASTER - FULL CONTROL MODE ACTIVATED")
        print(f"   Model: opencode/big-pickle")
        print(f"   Seed: {self.game_state['random_seed']}")
        print(f"   Personality: {self.game_state['ai_personality']}")
        print("="*60 + "\n")
    
    def ai_decide(self):
        """AI makes random decisions every tick"""
        decisions = []
        
        # Random enemy spawn (40% chance)
        if random.random() < 0.4:
            enemy = self.spawn_enemy()
            decisions.append(f"SPAWN: {enemy['type']} (HP:{enemy['health']})")
        
        # Random event (25% chance)
        if random.random() < 0.25:
            event = self.trigger_event()
            decisions.append(f"EVENT: {event['name']}")
        
        # Random world modification (30% chance)
        if random.random() < 0.3:
            mod = self.modify_world()
            decisions.append(f"MODIFY: {mod}")
        
        return decisions
    
    def spawn_enemy(self):
        """AI spawns enemy with random attributes"""
        types = ["Skulltula_Fighter", "Dark_Link_Interceptor", "Gohma_Carrier", 
                 "AI_Spawn", "Shadow_Clone", "Time_Wraith"]
        
        enemy = {
            "id": f"enemy_{self.tick}_{random.randint(100,999)}",
            "type": random.choice(types),
            "health": random.randint(10, 150),
            "damage": random.randint(5, 30),
            "speed": random.choice(["slow", "normal", "fast", "teleporting", "erratic"]),
            "behavior": random.choice(["aggressive", "defensive", "cowardly", "berserk"]),
            "ai_controlled": True,
            "spawned_at_tick": self.tick
        }
        
        self.game_state["enemies"].append(enemy)
        return enemy
    
    def trigger_event(self):
        """AI triggers random world events"""
        events = [
            {"name": "GRAVITY_FLIP", "effect": "gravity_inverted", "dialogue": "The laws of physics bend!"},
            {"name": "TIME_STOP", "effect": "bullet_time", "dialogue": "Time itself halts!"},
            {"name": "METEOR_SHOWER", "effect": "hazards_spawn", "dialogue": "The heavens rain fire!"},
            {"name": "WEAPON_RAIN", "effect": "powerups_spawn", "dialogue": "Gifts from the Goddesses!"},
            {"name": "BLACK_HOLE", "effect": "suck_entities", "dialogue": "A rift in space opens!"},
            {"name": "CLONE_ARMY", "effect": "spawn_ally", "dialogue": "You are not alone!"},
            {"name": "SPEED_DEMON", "effect": "player_speed_x3", "dialogue": "Feel the lightning!"},
            {"name": "INVINCIBILITY", "effect": "player_invincible", "dialogue": "The Triforce protects!"},
            {"name": "ENEMY_MADNESS", "effect": "enemies_berserk", "dialogue": "Madness takes hold!"},
            {"name": "DIMENSION_RIFT", "effect": "portals_everywhere", "dialogue": "Reality tears apart!"}
        ]
        
        event = random.choice(events)
        event["triggered_at_tick"] = self.tick
        event["duration"] = random.randint(10, 60)
        self.game_state["active_events"].append(event)
        self.game_state["world"]["event_active"] = event["name"]
        return event
    
    def modify_world(self):
        """AI modifies world parameters randomly"""
        modifications = [
            "difficulty_scaled", "area_changed", "weather_altered", 
            "physics_tweaked", "spawn_rate_adjusted"
        ]
        
        mod = random.choice(modifications)
        
        if mod == "difficulty_scaled":
            self.game_state["world"]["difficulty"] = random.randint(1, 10)
        elif mod == "area_changed":
            areas = ["Hyrule Space Station", "Zora Nebula", "Ganon's Death Star", "Shadow Realm", "Time Temple"]
            self.game_state["world"]["area"] = random.choice(areas)
        elif mod == "physics_tweaked":
            pass  # Would modify gravity, friction, etc.
        
        return mod
    
    def save_state(self):
        """Save current state for SoH to read"""
        state_file = os.path.expanduser("~/HylianModding/AI_DM/current_state.json")
        with open(state_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "tick": self.tick,
                "game_state": self.game_state,
                "ai_controller": "big-pickle",
                "dm_active": True,
                "random_mode": "CHAOS"
            }, f, indent=2)
    
    def run(self):
        """Main AI DM loop - controls EVERYTHING"""
        print("🧠 AI DM: Taking control of the game world...\n")
        
        try:
            while self.running:
                self.tick += 1
                self.game_state["world"]["time"] = self.tick
                
                # AI makes decisions
                decisions = self.ai_decide()
                
                # Display status
                event_active = self.game_state["world"].get("event_active") or "None"
                print(f"TICK {self.tick} | ", end="")
                print(f"Enemies:{len(self.game_state['enemies'])} | ", end="")
                print(f"Event:{event_active[:12]} | ", end="")
                print(f"Area:{self.game_state['world']['area'][:15]} | ", end="")
                print(f"Diff:{self.game_state['world']['difficulty']}")
                
                # Show AI decisions
                if decisions:
                    for d in decisions:
                        print(f"   🎲 AI DECISION: {d}")
                
                # Cleanup old events
                self.game_state["active_events"] = [
                    e for e in self.game_state["active_events"] 
                    if self.tick - e.get("triggered_at_tick", 0) < e.get("duration", 60)
                ]
                
                # Save state
                if self.tick % 5 == 0:
                    self.save_state()
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🧠 AI DM: Releasing control...")
            self.running = False
        
        self.save_state()
        print("\n🧠 AI DUNGEON MASTER SESSION ENDED")

if __name__ == "__main__":
    dm = AIDungeonMaster()
    dm.run()
