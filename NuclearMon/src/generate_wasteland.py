#!/usr/bin/env python3
"""
NuclearMon — Wasteland World Generator
Generates post-apocalyptic Pokémon war content for N64/Ship of Harkinian.
Extends the HylianModding AI World Architect pipeline.
"""

import os
import sys
import json
import random

sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_World"))
sys.path.insert(0, os.path.expanduser("~/HylianModding/AI_DM"))

import level_generator
import texture_packager

NUCLEAR_MON_DIR = os.path.expanduser("~/HylianModding/NuclearMon")
WORLDS_DIR = os.path.join(NUCLEAR_MON_DIR, "worlds")
LEVELS_DIR = os.path.join(NUCLEAR_MON_DIR, "levels")

# NuclearMon-specific content
WASTELAND_REGIONS = [
    {"id": "viridian_crater", "name": "Viridian Crater", "type": "crater", "rad_level": 10, "boss": "Nuclear Charizard"},
    {"id": "pallet_ruins", "name": "Pallet Ruins", "type": "village", "rad_level": 1, "boss": None},
    {"id": "mt_moon_mine", "name": "Mt. Moon Mine", "type": "mine", "rad_level": 6, "boss": "Glowing Onix"},
    {"id": "cerulean_canal", "name": "Cerulean Canal", "type": "water", "rad_level": 4, "boss": "Toxic Gyarados"},
    {"id": "saffron_scrapyard", "name": "Saffron Scrapyard", "type": "city", "rad_level": 3, "boss": "Toxic Mewtwo"},
    {"id": "cinnabar_reactor", "name": "Cinnabar Reactor", "type": "reactor", "rad_level": 10, "boss": "Nuclear Charizard"},
]

MUTATED_POKEMON = [
    {"name": "Rad-Rattata", "types": ["Normal", "Radiation"], "hp": 30, "moves": ["Tackle", "Rad Bite"], "mutation": 40},
    {"name": "Glowing Geodude", "types": ["Rock", "Radiation"], "hp": 40, "moves": ["Rollout", "Irradiate"], "mutation": 60},
    {"name": "Toxic Grimer", "types": ["Poison", "Nuclear"], "hp": 50, "moves": ["Sludge", "Meltdown"], "mutation": 80},
    {"name": "Feral Pidgey", "types": ["Flying", "Radiation"], "hp": 35, "moves": ["Gust", "Plume Strike"], "mutation": 35},
    {"name": "Volatile Voltorb", "types": ["Electric", "Nuclear"], "hp": 25, "moves": ["Spark", "Self-Destruct"], "mutation": 90},
    {"name": "Irradiated Ghastly", "types": ["Ghost", "Radiation"], "hp": 45, "moves": ["Lick", "Toxic Aura"], "mutation": 55},
    {"name": "Nuclear Charmander", "types": ["Fire", "Nuclear"], "hp": 65, "moves": ["Ember", "Atomic Breath"], "mutation": 75},
    {"name": "Mutated Bulbasaur", "types": ["Grass", "Radiation"], "hp": 60, "moves": ["Vine Whip", "Gamma Drain"], "mutation": 50},
    {"name": "Toxic Squirtle", "types": ["Water", "Poison"], "hp": 60, "moves": ["Water Gun", "Acid Spray"], "mutation": 45},
]

LEGENDARY_BOSSES = [
    {"name": "Nuclear Charizard", "types": ["Fire", "Nuclear"], "hp": 500, "moves": ["Wing Attack", "Fusion Flare", "Atomic Breath", "Meltdown"], "location": "cinnabar_reactor"},
    {"name": "Toxic Mewtwo", "types": ["Psychic", "Nuclear"], "hp": 600, "moves": ["Psychic", "Mind Blast", "Radiation Wave", "Psycho Cut"], "location": "saffron_scrapyard"},
    {"name": "Glowing Onix", "types": ["Rock", "Radiation"], "hp": 350, "moves": ["Rock Throw", "Irradiate", "Earthquake", "Hard Slam"], "location": "mt_moon_mine"},
    {"name": "Toxic Gyarados", "types": ["Water", "Nuclear"], "hp": 400, "moves": ["Hydro Pump", "Toxic Wave", "Dragon Rage", "Bite"], "location": "cerulean_canal"},
]

FACTIONS = [
    {"name": "The Silph Remnant", "alignment": "neutral", "trades": ["Military Ball", "Purification Chip"]},
    {"name": "The Rad Cult", "alignment": "hostile", "trades": ["Mutagen Syringe"]},
    {"name": "The Oak Enclave", "alignment": "friendly", "trades": ["Purification Chip", "RadAway"]},
    {"name": "The Rocket Reborn", "alignment": "hostile", "trades": []},
    {"name": "The Vault Dwellers", "alignment": "neutral", "trades": ["Stimpak", "Geiger Counter"]},
]


def generate_wasteland_world(difficulty=5):
    """Generate the complete NuclearMon wasteland world."""
    world = {
        "game": "NuclearMon",
        "theme": "wasteland",
        "difficulty": difficulty,
        "seed": random.randint(1, 999999),
        "regions": [],
        "factions": FACTIONS,
        "pokemon": MUTATED_POKEMON,
        "bosses": LEGENDARY_BOSSES,
        "items": [
            {"name": "Scrap Poké Ball", "type": "capture", "rarity": "common"},
            {"name": "Military Ball", "type": "capture", "rarity": "legendary"},
            {"name": "RadAway", "type": "medicine", "rarity": "uncommon"},
            {"name": "Mutagen Syringe", "type": "mutation", "rarity": "rare"},
            {"name": "Purification Chip", "type": "mutation", "rarity": "rare"},
            {"name": "Stimpak", "type": "medicine", "rarity": "common"},
            {"name": "Nuka-Cherry", "type": "medicine", "rarity": "common"},
            {"name": "Geiger Counter", "type": "tool", "rarity": "uncommon"},
        ],
        "story": generate_story(),
    }

    # Generate regions with levels
    for region_template in WASTELAND_REGIONS:
        region = {
            **region_template,
            "loot_tier": region_template["rad_level"],
            "enemies": random.sample([p["name"] for p in MUTATED_POKEMON], k=min(3, len(MUTATED_POKEMON))),
            "connections": [],
        }
        world["regions"].append(region)

    # Connect regions
    for i in range(len(world["regions"]) - 1):
        world["regions"][i]["connections"].append(world["regions"][i + 1]["id"])

    # Generate a dungeon level for each region
    os.makedirs(LEVELS_DIR, exist_ok=True)
    for region in world["regions"]:
        if region["type"] in ["crater", "mine", "reactor", "city"]:
            level = level_generator.generate_dungeon_grid(
                width=14 + difficulty,
                height=14 + difficulty,
                theme="shadow" if region["rad_level"] > 5 else "dungeon",
                difficulty=difficulty,
            )
            level["name"] = region["name"]
            level["rad_level"] = region["rad_level"]
            level["boss"] = region.get("boss")
            level_path = os.path.join(LEVELS_DIR, f"{region['id']}_level.json")
            with open(level_path, "w") as f:
                json.dump(level, f, indent=2)
            region["level_file"] = level_path

    # Save world manifest
    os.makedirs(WORLDS_DIR, exist_ok=True)
    manifest_path = os.path.join(WORLDS_DIR, f"nuclearmon_world_diff{difficulty}.json")
    with open(manifest_path, "w") as f:
        json.dump(world, f, indent=2)

    # Generate markdown readable version
    md_path = os.path.join(WORLDS_DIR, f"nuclearmon_world_diff{difficulty}.md")
    with open(md_path, "w") as f:
        f.write("# ☢️ NuclearMon: The Ashlands\n\n")
        f.write(f"**Difficulty:** {difficulty}/10  \n")
        f.write(f"**Seed:** {world['seed']}  \n\n")
        f.write("## Story\n\n")
        f.write(world["story"] + "\n\n")
        f.write("## Regions\n\n")
        for r in world["regions"]:
            f.write(f"### {r['name']} ({r['type']})\n")
            f.write(f"- Radiation Level: {r['rad_level']}/10\n")
            f.write(f"- Enemies: {', '.join(r['enemies'])}\n")
            f.write(f"- Boss: {r.get('boss', 'None')}\n")
            f.write(f"- Level File: `{r.get('level_file', 'N/A')}`\n\n")
        f.write("## Legendary Bosses\n\n")
        for b in world["bosses"]:
            f.write(f"- **{b['name']}** — HP: {b['hp']}, Types: {'/'.join(b['types'])}\n")
        f.write("\n## Factions\n\n")
        for fa in world["factions"]:
            f.write(f"- **{fa['name']}** — {fa['alignment'].title()}\n")
        f.write("\n## Mutated Pokémon Roster\n\n")
        for p in world["pokemon"]:
            f.write(f"- **{p['name']}** — Types: {'/'.join(p['types'])}, Mutation: {p['mutation']}%\n")

    print(f"[NuclearMon] World generated: {manifest_path}")
    print(f"[NuclearMon] Readable docs: {md_path}")
    return world


def generate_story():
    """Generate the NuclearMon backstory."""
    intros = [
        "Thirty years ago, the Great War scorched Kanto. The missiles fell on Cinnabar, on Saffron, on the Pokémon League itself.",
        "When the skies burned green, the Pokémon didn't die. They changed. Mutated. Became something new and terrible.",
        "Professor Oak's final broadcast warned us: 'The Pokémon are no longer our friends. They are survivors, like us. And survivors are dangerous.'",
    ]
    middles = [
        "Now, Poké Balls are currency. Pure-strain Pokémon are myths. And in the crater where Viridian City once stood, something vast stirs beneath the ash.",
        "The Silph Remnant controls the last manufacturing line. The Rad Cult worships the glowing Pokémon as gods. And somewhere in the reactor ruins, a Charizard burns with the fire of a thousand suns.",
        "You were born in Pallet Ruins, sucking irradiated air. Your first Pokémon was a Rattata with three eyes and a temper. But it's yours. And in the wasteland, that's enough.",
    ]
    endings = [
        "Gotta catch 'em all... before the radiation catches you.",
        "The war is over. The Pokémon war has just begun.",
        "In the Ashlands, there are no gyms. Only graves. And graves make excellent Poké Ball material.",
    ]
    return f"{random.choice(intros)} {random.choice(middles)} {random.choice(endings)}"


def generate_texture_pack():
    """Create a post-apocalyptic texture pack for SoH using Classic64 assets."""
    print("[NuclearMon] Building wasteland texture pack...")
    # Use the existing texture packager but with a custom theme filter
    pack_name = "nuclearmon_wasteland"
    output_dir = os.path.join(NUCLEAR_MON_DIR, "textures", pack_name)
    os.makedirs(output_dir, exist_ok=True)

    # Scan Classic64 for wasteland-appropriate textures
    classic64_dirs = [
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Ground",
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Nature",
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Industrial",
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Metal",
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Rocks",
        "/home/donn/Downloads/- Classic 64 Asset Pack 0.6/Road",
    ]

    collected = []
    for d in classic64_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(('.png', '.jpg', '.bmp')):
                    collected.append(os.path.join(d, f))

    # Create a manifest
    manifest = {
        "name": pack_name,
        "description": "Post-apocalyptic Pokémon wasteland textures for NuclearMon",
        "source": "Classic64 Asset Pack",
        "texture_count": len(collected),
        "textures": [os.path.basename(p) for p in collected],
    }
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[NuclearMon] Texture pack manifest: {len(collected)} textures cataloged")
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NuclearMon Wasteland Generator")
    parser.add_argument("--difficulty", type=int, default=5, help="World difficulty 1-10")
    parser.add_argument("--textures", action="store_true", help="Generate texture pack manifest")
    args = parser.parse_args()

    world = generate_wasteland_world(args.difficulty)
    if args.textures:
        generate_texture_pack()
