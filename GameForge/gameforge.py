#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🎮 AI GAMEFORGE 🎮                                  ║
║         Multi-Platform Game & Mod Generator for NuclearMon / StellarMon       ║
║                  N64 | PS1 | PS2 | Xbox 360 | PC (Retro Aesthetic)            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage:
  ./gameforge.py concept --franchise nuclearmon --platform n64
  ./gameforge.py mod --base oot --theme wasteland --output ./mods/
  ./gameforge.py story --arc moonfall --chapters 5
  ./gameforge.py campaign --games nuclearmon,stellarmon --event bigbang
  ./gameforge.py list-platforms
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime

FORGE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(FORGE_DIR, "outputs")
MODELS_DIR = os.path.expanduser("~/Downloads/models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

PLATFORMS = {
    "n64": {
        "name": "Nintendo 64",
        "poly_budget": 1500,
        "texture_size": "32x32 to 64x64",
        "color_depth": "16-bit",
        "audio": "16-channel MIDI + compressed samples",
        "engine": "libdragon / OoT Decomp / ModLoader64 / Ship of Harkinian",
        "file_format": ".z64 / .o2r / .ml64mod",
        "aesthetic": "Low-poly, heavy fog, point-filtered textures, 320x240",
        "controls": "Analog stick + A/B/Z + C-buttons + R/L",
    },
    "ps1": {
        "name": "PlayStation 1",
        "poly_budget": 1200,
        "texture_size": "256x256 max",
        "color_depth": "24-bit color, 256 color palettes",
        "audio": "XA-ADPCM streaming, MIDI",
        "engine": "PSn00bSDK / Unity (retro shader) / Godot",
        "file_format": ".bin / .cue / .pbp",
        "aesthetic": "Affine texture wobble, vertex jitter, dithering, low FPS",
        "controls": "D-Pad / Analog (DualShock) + X/O/□/△ + L1/R1/L2/R2",
    },
    "ps2": {
        "name": "PlayStation 2",
        "poly_budget": 8000,
        "texture_size": "512x512",
        "color_depth": "32-bit",
        "audio": "ADPCM stereo, streaming",
        "engine": "ps2sdk / Unity / Godot / PCSX2 modding",
        "file_format": ".iso / .elf",
        "aesthetic": "Bloom, motion blur, cinematic camera, early shaders",
        "controls": "DualShock 2 full analog + pressure sensitive buttons",
    },
    "xbox360": {
        "name": "Xbox 360",
        "poly_budget": 50000,
        "texture_size": "1024x1024",
        "color_depth": "HDR, 720p",
        "audio": "5.1 surround, XMA compression",
        "engine": "XNA / Unity / Unreal / Xenon homebrew",
        "file_format": ".xex / .iso",
        "aesthetic": "Normal maps, specular highlights, achievements, leaderboards",
        "controls": "Xbox 360 controller + triggers + bumpers + guide button",
    },
    "pc_retro": {
        "name": "PC (Retro Aesthetic)",
        "poly_budget": 1500,
        "texture_size": "64x64",
        "color_depth": "16-bit simulated",
        "audio": "Ogg Vorbis, chiptune optional",
        "engine": "Ursina / Godot / Unity + CRT shaders",
        "file_format": ".exe / .app / .zip",
        "aesthetic": "Configurable: N64 fog, PS1 wobble, scanlines, bezel",
        "controls": "Keyboard + Mouse or any gamepad",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FRANCHISE DATA
# ═══════════════════════════════════════════════════════════════════════════════

FRANCHISES = {
    "nuclearmon": {
        "title": "NuclearMon: Ashlands",
        "subtitle": "Post-Nuclear Pokémon War",
        "genre": "Action RPG / Creature Collector / Survival",
        "setting": " irradiated ruins of Kanto, 30 years after The Flash",
        "tone": "Grim, desperate, darkly humorous",
        "core_mechanic": "Real-time Pokémon combat with radiation mutation system",
        "starter_pokemon": ["Mutated Bulbasaur", "Nuclear Charmander", "Toxic Squirtle"],
        "legendary": "Nuclear Charizard (Cinnabar Reactor)",
        "factions": ["Silph Remnant", "Rad Cult", "Oak Enclave", "Rocket Reborn", "Vault Dwellers"],
        "key_items": ["Scrap Poké Ball", "RadAway", "Mutagen Syringe", "Geiger Counter"],
        "environments": ["Viridian Crater", "Pallet Ruins", "Mt. Moon Mine", "Cerulean Canal", "Saffron Scrapyard", "Cinnabar Reactor"],
    },
    "stellarmon": {
        "title": "StellarMon: Moonfall",
        "subtitle": "When the Moon Killed the World",
        "genre": "Space Exploration RPG / Colony Sim / Creature Collector",
        "setting": "Earth's shattered remains and the orbital colonies 200 years after Moonfall",
        "tone": "Hopeful, cosmic horror, wonder",
        "core_mechanic": "Build space colonies, terraform worlds, discover cosmic Pokémon variants",
        "starter_pokemon": ["Void Eevee", "Lunar Cubone", "Comet Clefairy"],
        "legendary": "Eclipse Mewtwo (Dark Side of the Moon base)",
        "factions": ["Lunar Collective", "Terran Remnant", "The Void Breeders", "Aether Corp", "Starbound Rangers"],
        "key_items": ["Vacuum Ball", "Oxygen Tank", "Terraforming Seed", "Warp Drive"],
        "environments": ["Shattered Earth Orbit", "Lunar Colony Alpha", "Mars Terraform Zone", "Asteroid Belt Gyms", "Deep Space Void", "The Eclipse Station"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# LLM INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_llm():
    try:
        from llama_cpp import Llama
    except ImportError:
        print("[GameForge] llama-cpp-python not available")
        return None
    candidates = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
    if not candidates:
        return None
    # Prefer larger models for creative writing
    candidates.sort(key=lambda x: os.path.getsize(os.path.join(MODELS_DIR, x)), reverse=True)
    model_path = os.path.join(MODELS_DIR, candidates[0])
    print(f"[GameForge] Loading LLM: {candidates[0]}")
    return Llama(model_path=model_path, n_ctx=4096, verbose=False)


def llm_generate(prompt, max_tokens=800):
    llm = get_llm()
    if not llm:
        return "[LLM unavailable - install a .gguf model in ~/Downloads/models]"
    try:
        output = llm(prompt, max_tokens=max_tokens, stop=["</s>", "User:", "###"])
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"[LLM error: {e}]"


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_concept(franchise_key, platform_key, use_llm=True):
    """Generate a complete game concept document."""
    franchise = FRANCHISES[franchise_key]
    platform = PLATFORMS[platform_key]

    print(f"\n[GameForge] Generating concept: {franchise['title']} for {platform['name']}\n")

    concept = {
        "generated_at": datetime.now().isoformat(),
        "franchise": franchise_key,
        "platform": platform_key,
        "title": franchise["title"],
        "subtitle": franchise["subtitle"],
        "genre": franchise["genre"],
        "platform_specs": {
            "poly_budget": platform["poly_budget"],
            "texture_size": platform["texture_size"],
            "color_depth": platform["color_depth"],
            "engine": platform["engine"],
            "aesthetic": platform["aesthetic"],
        },
        "story_hook": generate_story_hook(franchise_key, use_llm),
        "core_loop": generate_core_loop(franchise_key, platform_key),
        "environments": franchise["environments"],
        "factions": franchise["factions"],
        "starter_pokemon": franchise["starter_pokemon"],
        "legendary_boss": franchise["legendary"],
        "key_items": franchise["key_items"],
        "controls": platform["controls"],
        "chapters": generate_chapters(franchise_key, use_llm),
        "mod_ideas": generate_mod_ideas(franchise_key, platform_key),
    }

    # Save
    filename = f"{franchise_key}_{platform_key}_concept.json"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(concept, f, indent=2)

    # Markdown readable
    md_path = os.path.join(OUTPUT_DIR, f"{franchise_key}_{platform_key}_concept.md")
    with open(md_path, "w") as f:
        f.write(f"# {concept['title']}\n")
        f.write(f"*{concept['subtitle']}* — {platform['name']} Edition\n\n")
        f.write(f"## Story Hook\n\n{concept['story_hook']}\n\n")
        f.write(f"## Core Gameplay Loop\n\n{concept['core_loop']}\n\n")
        f.write(f"## Chapters\n\n")
        for i, ch in enumerate(concept['chapters'], 1):
            f.write(f"### Chapter {i}: {ch['title']}\n")
            f.write(f"{ch['summary']}\n\n")
            f.write(f"- **Location:** {ch['location']}\n")
            f.write(f"- **Boss:** {ch['boss']}\n")
            f.write(f"- **New Mechanic:** {ch['mechanic']}\n\n")
        f.write(f"## Mod Ideas\n\n")
        for mod in concept['mod_ideas']:
            f.write(f"- **{mod['name']}**: {mod['description']} ({mod['complexity']})\n")

    print(f"[GameForge] Concept saved to: {path}")
    print(f"[GameForge] Readable docs: {md_path}")
    return concept


def generate_story_hook(franchise, use_llm=True):
    if franchise == "nuclearmon":
        base = (
            "Thirty years ago, the Great War scorched Kanto. The missiles fell on Cinnabar, "
            "on Saffron, on the Pokémon League itself. When the skies burned green, the Pokémon didn't die. "
            "They changed. Mutated. Became something new and terrible. Now, Poké Balls are currency. "
            "Pure-strain Pokémon are myths. And in the crater where Viridian City once stood, "
            "something vast stirs beneath the ash."
        )
    elif franchise == "stellarmon":
        base = (
            "200 years ago, the Moon fell. Not an impact—a transformation. Luna cracked open like an egg, "
            "and from it poured the Cosmic Seeds: dormant Pokémon DNA from before Earth's formation. "
            "The world was reshaped. Gravity failed in places. The oceans floated. "
            "Humanity fled to orbital colonies. Now, you are a Starbound Ranger, "
            "taming Void Pokémon in the wreckage of old Earth and the colonies beyond. "
            "But something is waking on the dark side of the Moon. Something that remembers."
        )
    else:
        base = "[Unknown franchise]"

    if use_llm:
        prompt = f"Rewrite this game story hook to be more atmospheric and compelling (3-4 sentences):\n\n{base}\n\nImproved version:"
        improved = llm_generate(prompt, max_tokens=300)
        if not improved.startswith("["):
            return improved
    return base


def generate_core_loop(franchise, platform):
    if franchise == "nuclearmon":
        return (
            f"1. Explore the wasteland (third-person, {platform} controls)\n"
            f"2. Engage mutated Pokémon in real-time combat (Z-target + C-button moves)\n"
            f"3. Weaken and capture using scarce Poké Balls\n"
            f"4. Manage radiation exposure and Pokémon mutation levels\n"
            f"5. Scavenge, craft, and trade with factions\n"
            f"6. Uncover the truth behind The Flash"
        )
    elif franchise == "stellarmon":
        return (
            f"1. Pilot your colony ship between orbital zones (space map)\n"
            f"2. Land on shattered Earth fragments or colony stations\n"
            f"3. Discover and tame Cosmic Pokémon variants (Vacuum Balls)\n"
            f"4. Build colonies, manage oxygen, grow food\n"
            f"5. Defend against Void Breeder raids\n"
            f"6. Unlock warp gates to reach the Moon and confront Eclipse Mewtwo"
        )
    return "[Unknown core loop]"


def generate_chapters(franchise, use_llm=True):
    if franchise == "nuclearmon":
        chapters = [
            {"title": "The Cradle", "location": "Pallet Ruins", "boss": "Rad-Rattata Pack Alpha", "mechanic": "Basic combat & capture", "summary": "You wake in Pallet Ruins. Professor Oak's AI hologram gives you your first pure-strain starter and warns you about the crater."},
            {"title": "Into the Ash", "location": "Viridian Crater Edge", "boss": "Glowing Onix", "mechanic": "Radiation zones & RadAway", "summary": "Your first journey into high-rad territory. The Geiger Counter becomes essential. You discover the Rad Cult performing rituals."},
            {"title": "The Silph Gate", "location": "Saffron Scrapyard", "boss": "Mecha-Rhydon", "mechanic": "Faction reputation & trading", "summary": "The Silph Remnant controls Poké Ball manufacturing. Help them, and gain access to Military Balls. Cross them, and face their mechs."},
            {"title": "Canal of Ghosts", "location": "Cerulean Canal", "boss": "Toxic Gyarados", "mechanic": "Underwater/aquatic combat", "summary": "The flooded city hides pre-war tech. The water-types here are bioluminescent horrors. Oak Enclave needs samples."},
            {"title": "Mine of Whispers", "location": "Mt. Moon Mine", "boss": "Glowing Onix Prime", "mechanic": "Cave exploration & light management", "summary": "Uranium veins run through the old caves. The deeper you go, the more mutated the Pokémon. A Vault Dweller settlement needs rescue."},
            {"title": "Meltdown", "location": "Cinnabar Reactor", "boss": "Nuclear Charizard", "mechanic": "Final boss: mutation purging & legendary capture", "summary": "The reactor core still burns. Nuclear Charizard nests here, absorbing radiation for decades. This is the end—or the beginning."},
        ]
    elif franchise == "stellarmon":
        chapters = [
            {"title": "Orphan of Earth", "location": "Shattered Earth Orbit", "boss": "Gravity-Titan Snorlax", "mechanic": "Zero-G movement & Vacuum Ball capture", "summary": "You were born on Colony 7. Your first mission: retrieve a drifting Poké Ball manufacturing satellite. Inside: a Void Eevee."},
            {"title": "Lunar Shadow", "location": "Lunar Colony Alpha", "boss": "Lunar Marowak", "mechanic": "Oxygen management & colony building", "summary": "The Moon colonies are failing. Terraform the surface, establish oxygen generators, and discover why colonists are vanishing."},
            {"title": "Red Dust", "location": "Mars Terraform Zone", "boss": "Terraform Tyranitar", "mechanic": "Terraforming minigame & agriculture", "summary": "Mars is halfway habitable. Plant Terraforming Seeds, defend against dust storms, and find the ancient Pokémon buried in Olympus Mons."},
            {"title": "The Belt", "location": "Asteroid Belt Gyms", "boss": "Asteroid Champion Machamp", "mechanic": "Six-on-six space gym battles", "summary": "The Asteroid Belt is lawless. Pirate gyms rule individual rocks. Earn the 8 Belt Badges to unlock the warp gate."},
            {"title": "Void Breach", "location": "Deep Space Void", "boss": "Void Legendary Rayquaza", "mechanic": "Ship combat & boarding parties", "summary": "The Void Breeders attack in force. Their ships are grown, not built—bio-mechanical Pokémon hybrids. Board them. Capture them."},
            {"title": "The Eclipse", "location": "The Eclipse Station", "boss": "Eclipse Mewtwo", "mechanic": "Reality-warping final battle", "summary": "On the dark side of the Moon, Eclipse Mewtwo waits. It remembers Earth. It remembers you. The Cosmic Seed must be planted—or destroyed."},
        ]
    else:
        chapters = []

    if use_llm:
        for ch in chapters:
            prompt = f"Rewrite this game chapter summary to be more atmospheric (2-3 sentences):\n\nTitle: {ch['title']}\nSummary: {ch['summary']}\n\nImproved:"
            improved = llm_generate(prompt, max_tokens=200)
            if not improved.startswith("["):
                ch["summary"] = improved

    return chapters


def generate_mod_ideas(franchise, platform):
    """Generate mod concepts that the Game Forge could build."""
    common_mods = [
        {"name": "Hardcore Mode", "description": "Permadeath. No RadAway. Poké Balls break after 3 uses.", "complexity": "Easy"},
        {"name": "New Game+", "description": "Carry over mutation research. Enemies scale. New legendary spawns.", "complexity": "Medium"},
        {"name": "Co-op Companion", "description": "Second player controls your lead Pokémon in split-screen.", "complexity": "Hard"},
    ]
    if franchise == "nuclearmon":
        specific = [
            {"name": "The Vaults", "description": "10 underground dungeon maps with pre-war loot and pure-strain Pokémon.", "complexity": "Medium"},
            {"name": "Nuka-Cherry Overhaul", "description": "Add addiction system. Too much healing causes hallucination battles.", "complexity": "Medium"},
            {"name": "Rocket Reborn Uprising", "description": "New faction war questline. Capture or destroy Rocket bases.", "complexity": "Hard"},
            {"name": "Ghastly Nights", "description": "Night-only survival mode. Ghost/Radiation types swarm. Build defenses.", "complexity": "Medium"},
        ]
    elif franchise == "stellarmon":
        specific = [
            {"name": "Satellite Defense", "description": "Tower defense mod for colony ships. Deploy Pokémon as turrets.", "complexity": "Medium"},
            {"name": "The Outer Rim", "description": "Procedurally generated planets beyond the Belt. Infinite exploration.", "complexity": "Hard"},
            {"name": "Cosmic Breeding", "description": "Breed Pokémon in zero-G for rare cosmic-type variants.", "complexity": "Medium"},
            {"name": "Holodeck Challenges", "description": "Simulated Earth environments. Nostalgia-driven puzzle dungeons.", "complexity": "Easy"},
        ]
    else:
        specific = []
    return common_mods + specific


def generate_crossover_event(games, use_llm=True):
    """Generate a crossover event linking multiple games."""
    print(f"\n[GameForge] Generating crossover event for: {', '.join(games)}\n")

    event = {
        "title": "THE BIG BANG CROSSOVER EVENT",
        "games_involved": games,
        "generated_at": datetime.now().isoformat(),
        "premise": (
            "In every timeline, the Moon watches. In NuclearMon's timeline, it was silent during The Flash—"
            "but astronomers noted it pulsed green. In StellarMon's timeline, it cracked open. "
            "The truth: they are the SAME Moon, across divergent timelines. The Big Bang Event is the moment "
            "when a Trainer in the Ashlands discovers an ancient Silph prototype—the CHRONOS BALL—and catches "
            "a Pokémon that exists outside time. The catch creates a paradox. The timelines bleed. "
            "Nuclear Charizard's radiation reaches space. Eclipse Mewtwo's psychic scream echoes backward through time. "
            "And a new legendary is born: BIG BANG ARCEUS, the Pokémon that existed before the universe, "
            "now furious that mortals have weaponized its children."
        ),
        "phases": [
            {"phase": 1, "name": "The Signal", "description": "Players in both games receive a mysterious transmission. In NuclearMon: a radio signal from space. In StellarMon: an ancient Earth broadcast."},
            {"phase": 2, "name": "The Breach", "description": "A portal opens. NuclearMon trainers see space Pokémon in the wasteland. StellarMon rangers find ash-covered, mutated Pokémon on colony ships."},
            {"phase": 3, "name": "The Paradox", "description": "Catching a crossover Pokémon in one game makes it appear in the other—with transformed stats and types."},
            {"phase": 4, "name": "The Convergence", "description": "Both games unlock a shared final dungeon: The Lunar Core. Requires save data from both games to enter."},
            {"phase": 5, "name": "The Big Bang", "description": "Battle Big Bang Arceus. It uses moves from both games. Victory unlocks the CHRONOS BALL in both save files permanently."},
        ],
        "crossover_pokemon": [
            {"name": "Void-Rad Charizard", "origin": "NuclearMon → StellarMon", "type": "Fire/Nuclear/Void", "lore": "A Charizard that absorbed so much radiation it punched through reality and now drifts in the void between stars."},
            {"name": "Lunar Mewtwo", "origin": "StellarMon → NuclearMon", "type": "Psychic/Cosmic", "lore": "Eclipse Mewtwo's psychic projection, sent backward in time to prevent The Flash. It failed. It stayed."},
            {"name": "Big Bang Arceus", "origin": "Both", "type": "Normal/Cosmic/Nuclear", "lore": "The Original One, angered by the corruption of its creations across all timelines."},
        ],
        "rewards": {
            "nuclearmon": ["Chronos Ball", "Space Suit armor", "Starbound Ranger companion skin"],
            "stellarmon": ["Chronos Ball", "Wasteland Survivor suit", "Ashlands Charizard mount skin"],
        },
    }

    if use_llm:
        prompt = (
            "Write an epic 4-paragraph crossover event description for two Pokémon games: "
            "NuclearMon (post-nuclear wasteland) and StellarMon (space colonies after the Moon destroys Earth). "
            "The event is called THE BIG BANG. A legendary Pokémon named Big Bang Arceus threatens both timelines. "
            "Make it cinematic, mysterious, and hype-building. End with a tagline."
        )
        event["narrative"] = llm_generate(prompt, max_tokens=600)
    else:
        event["narrative"] = event["premise"]

    path = os.path.join(OUTPUT_DIR, "bigbang_crossover_event.json")
    with open(path, "w") as f:
        json.dump(event, f, indent=2)

    md_path = os.path.join(OUTPUT_DIR, "bigbang_crossover_event.md")
    with open(md_path, "w") as f:
        f.write(f"# ☄️ {event['title']}\n\n")
        f.write(f"{event['narrative']}\n\n")
        f.write("## Event Phases\n\n")
        for ph in event["phases"]:
            f.write(f"### Phase {ph['phase']}: {ph['name']}\n")
            f.write(f"{ph['description']}\n\n")
        f.write("## Crossover Pokémon\n\n")
        for p in event["crossover_pokemon"]:
            f.write(f"- **{p['name']}** ({p['origin']}) — *{p['type']}*\n  {p['lore']}\n\n")
        f.write("## Rewards\n\n")
        for game, rewards in event["rewards"].items():
            f.write(f"- **{game.title()}**: {', '.join(rewards)}\n")

    print(f"[GameForge] Crossover event saved to: {path}")
    print(f"[GameForge] Readable docs: {md_path}")
    return event


def list_platforms():
    print("\n[GameForge] Supported Platforms\n")
    for key, p in PLATFORMS.items():
        print(f"  {key:12} | {p['name']:20} | Engine: {p['engine']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="AI GameForge — Multi-Platform Game & Mod Generator")
    subparsers = parser.add_subparsers(dest="command")

    p_concept = subparsers.add_parser("concept", help="Generate a game concept")
    p_concept.add_argument("--franchise", choices=list(FRANCHISES.keys()), required=True)
    p_concept.add_argument("--platform", choices=list(PLATFORMS.keys()), required=True)
    p_concept.add_argument("--no-llm", action="store_true")

    p_story = subparsers.add_parser("story", help="Generate story arc")
    p_story.add_argument("--arc", choices=["moonfall", "ashlands", "bigbang"], required=True)
    p_story.add_argument("--chapters", type=int, default=5)

    p_campaign = subparsers.add_parser("campaign", help="Generate crossover campaign")
    p_campaign.add_argument("--games", required=True, help="Comma-separated franchise keys")
    p_campaign.add_argument("--event", default="bigbang")
    p_campaign.add_argument("--no-llm", action="store_true")

    p_list = subparsers.add_parser("list-platforms", help="List supported platforms")

    args = parser.parse_args()

    if args.command == "concept":
        generate_concept(args.franchise, args.platform, not args.no_llm)
    elif args.command == "story":
        print(f"[GameForge] Story arc: {args.arc} ({args.chapters} chapters)")
    elif args.command == "campaign":
        games = [g.strip() for g in args.games.split(",")]
        generate_crossover_event(games, not args.no_llm)
    elif args.command == "list-platforms":
        list_platforms()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
