#!/usr/bin/env python3
"""
N64 AI Co-op Lab — AI Story Generator
======================================
Generates complete game worlds, stories, characters, and quests
using local LLMs and the ROM library as inspiration.
"""

import os
import json
import random
import sys

sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))

METADATA_DIR = os.path.expanduser("~/HylianModding/Library/Metadata")
OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/generated_stories")
MODELS_DIR = os.path.expanduser("~/Downloads/models")

# Theme palettes derived from owned ROMs
THEME_PALETTES = {
    "fantasy": {"colors": ["#2E8B57", "#8B4513", "#FFD700", "#4B0082"], "mood": "epic, magical"},
    "sci-fi": {"colors": ["#00FFFF", "#FF00FF", "#1E90FF", "#000000"], "mood": "futuristic, cold"},
    "horror": {"colors": ["#8B0000", "#2F2F2F", "#556B2F", "#000000"], "mood": "dark, oppressive"},
    "jungle": {"colors": ["#228B22", "#8B4513", "#FFD700", "#006400"], "mood": "lush, ancient"},
    "space": {"colors": ["#000080", "#4B0082", "#FFFFFF", "#00FFFF"], "mood": "vast, mysterious"},
    "cyberpunk": {"colors": ["#FF00FF", "#00FFFF", "#FFFF00", "#000000"], "mood": "neon, dystopian"},
    "gothic": {"colors": ["#2F2F2F", "#8B0000", "#4B0082", "#C0C0C0"], "mood": "haunting, grand"},
    "cartoon": {"colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"], "mood": "bright, playful"},
}


def load_llm(model_name=None):
    """Load a local GGUF model for inference."""
    try:
        from llama_cpp import Llama
    except ImportError:
        print("[StoryGen] llama-cpp-python not installed")
        return None
    
    if model_name:
        model_path = os.path.join(MODELS_DIR, model_name)
    else:
        # Pick first available
        candidates = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
        if not candidates:
            return None
        model_path = os.path.join(MODELS_DIR, candidates[0])
    
    if not os.path.exists(model_path):
        return None
    
    return Llama(model_path=model_path, n_ctx=4096, verbose=False)


def generate_world_seed(theme="fantasy", difficulty=3):
    """Generate a complete world definition using LLM + procedural mix."""
    palette = THEME_PALETTES.get(theme, THEME_PALETTES["fantasy"])
    
    world = {
        "theme": theme,
        "difficulty": difficulty,
        "palette": palette,
        "seed": random.randint(1, 999999),
        "regions": [],
        "factions": [],
        "key_items": [],
        "bosses": [],
    }
    
    # Procedural region generation
    region_types = ["forest", "mountain", "dungeon", "ruins", "cave", "temple", "castle", "village", "swamp", "desert"]
    num_regions = 3 + difficulty
    
    for i in range(num_regions):
        region = {
            "id": f"region_{i}",
            "name": f"{theme.title()} {random.choice(['Reach', 'Depths', 'Hollow', 'Pass', 'Gate', 'Vault', 'Wilds', 'Spire'])}",
            "type": random.choice(region_types),
            "connections": [],
            "enemies": [],
            "loot_tier": min(i + 1, 10),
        }
        world["regions"].append(region)
    
    # Connect regions (simple chain + random branches)
    for i in range(len(world["regions"]) - 1):
        world["regions"][i]["connections"].append(world["regions"][i+1]["id"])
        if random.random() > 0.5 and i > 0:
            target = random.randint(0, i)
            world["regions"][i]["connections"].append(world["regions"][target]["id"])
    
    # Generate factions
    faction_names = ["Order", "Cult", "Guild", "Tribe", "Empire", "Collective", "Swarm", "Circle"]
    for i in range(2 + difficulty // 3):
        world["factions"].append({
            "name": f"The {random.choice(faction_names)} of {random.choice(['Shadow', 'Light', 'Flame', 'Ice', 'Storm', 'Echo'])}",
            "alignment": random.choice(["friendly", "neutral", "hostile"]),
            "resources": random.sample(["gold", "magic", "tech", "artifacts", "information"], k=2),
        })
    
    # Generate bosses
    boss_titles = ["Lord", "Queen", "Overseer", "Harbinger", "Warden", "Tyrant", "Specter"]
    for i in range(1 + difficulty // 2):
        world["bosses"].append({
            "name": f"{random.choice(boss_titles)} {random.choice(['Xarath', 'Morwen', 'Kael', 'Vexis', 'Zelos', 'Nyra', 'Thalos'])}",
            "region": world["regions"][min(i, len(world["regions"])-1)]["id"],
            "hp": 50 + difficulty * 25,
            "weakness": random.choice(["fire", "ice", "light", "shadow", "explosive"]),
        })
    
    return world


def generate_story(world, llm=None):
    """Generate narrative text for the world."""
    if llm:
        prompt = f"""Write a dark fantasy backstory for a N64-style game world called the "{world['theme'].title()} Realms".
The world has {len(world['regions'])} regions and difficulty {world['difficulty']}.
Key factions: {', '.join(f['name'] for f in world['factions'][:2])}.
Main antagonist: {world['bosses'][0]['name']}.
Write 3 paragraphs. Keep it under 200 words. Style: atmospheric, mysterious, like Zelda Ocarina of Time.

Story:"""
        try:
            output = llm(prompt, max_tokens=400, stop=["</s>"])
            story = output["choices"][0]["text"].strip()
        except Exception as e:
            story = f"[LLM failed: {e}]"
    else:
        # Fallback procedural story
        story = (
            f"In the {world['theme']} realms, darkness spreads from the domain of {world['bosses'][0]['name']}. "
            f"The {world['factions'][0]['name']} seeks aid, while the {world['factions'][1]['name']} plots in shadow. "
            f"Only through the {len(world['regions'])} forbidden regions can the ancient seal be restored."
        )
    
    world["story"] = story
    return world


def generate_quests(world, count=5):
    """Generate quest definitions."""
    quest_types = ["fetch", "defeat", "explore", "escort", "puzzle", "collection"]
    quests = []
    
    for i in range(count):
        qtype = random.choice(quest_types)
        region = random.choice(world["regions"])
        quest = {
            "id": f"quest_{i}",
            "type": qtype,
            "region": region["id"],
            "giver": random.choice([f["name"] for f in world["factions"] if f["alignment"] != "hostile"] or ["Mysterious Stranger"]),
            "reward": random.choice(["key", "weapon", "heart_piece", "magic", "map"]),
            "description": f"{qtype.title()} in {region['name']}",
        }
        quests.append(quest)
    
    world["quests"] = quests
    return world


def save_world(world, name=None):
    """Save world definition to JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not name:
        name = f"{world['theme']}_diff{world['difficulty']}_seed{world['seed']}"
    
    path = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(world, f, indent=2)
    
    # Also save a markdown readable version
    md_path = os.path.join(OUTPUT_DIR, f"{name}.md")
    with open(md_path, "w") as f:
        f.write(f"# {world['theme'].title()} Realms\n\n")
        f.write(f"**Difficulty:** {world['difficulty']}/10  \n")
        f.write(f"**Seed:** {world['seed']}  \n")
        f.write(f"**Palette:** {', '.join(world['palette']['colors'])}  \n\n")
        f.write(f"## Story\n\n{world.get('story', 'No story generated.')}\n\n")
        f.write("## Regions\n\n")
        for r in world["regions"]:
            f.write(f"### {r['name']} ({r['type']})\n")
            f.write(f"- Loot Tier: {r['loot_tier']}\n")
            f.write(f"- Connections: {', '.join(r['connections']) or 'None'}\n\n")
        f.write("## Bosses\n\n")
        for b in world["bosses"]:
            f.write(f"- **{b['name']}** — HP: {b['hp']}, Weakness: {b['weakness']}\n")
        f.write("\n## Quests\n\n")
        for q in world["quests"]:
            f.write(f"- [{q['type'].upper()}] {q['description']} — Reward: {q['reward']}\n")
    
    return path


def build_complete_world(theme="fantasy", difficulty=3, use_llm=True):
    """Full pipeline: generate world + story + quests, save everything."""
    llm = load_llm() if use_llm else None
    world = generate_world_seed(theme, difficulty)
    world = generate_story(world, llm)
    world = generate_quests(world)
    path = save_world(world)
    print(f"[StoryGen] World saved to {path}")
    return world


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default="fantasy")
    parser.add_argument("--difficulty", type=int, default=3)
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()
    
    build_complete_world(args.theme, args.difficulty, not args.no_llm)
