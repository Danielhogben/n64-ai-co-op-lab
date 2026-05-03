#!/usr/bin/env python3
"""
N64 AI Co-op Lab — AI World Architect
======================================
The master orchestrator that creates complete game worlds from scratch.
Combines:
  - ROM library themes (298 games)
  - Procedural level generation (dungeon grids → 3D meshes)
  - AI story generation (local LLM)
  - Texture pack curation (61,000+ textures)
  - Asset scraping (live web discovery)
  - Swarm distribution (coordinated task generation)

Usage:
  ./world_architect.py --build --theme shadow --difficulty 5
  ./world_architect.py --campaign --rounds 3
  ./world_architect.py --catalog
  ./world_architect.py --scrape
"""

import os
import sys
import json
import random
import argparse

# Add sibling modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rom_library
import story_generator
import level_generator
import texture_packager
import asset_scraper

METADATA_DIR = os.path.expanduser("~/HylianModding/Library/Metadata")
MYWORLD_DIR = os.path.expanduser("~/HylianModding/MyWorld")


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🏰 N64 AI WORLD ARCHITECT 🏰                       ║
║     Creates entire worlds from 298 ROMs + 61K textures       ║
╚══════════════════════════════════════════════════════════════╝
""")


def build_world(theme, difficulty, use_llm=True):
    """Build a complete world: story + levels + textures."""
    print(f"\n[Architect] Building world: theme={theme}, difficulty={difficulty}")
    
    # 1. Generate story world
    world = story_generator.build_complete_world(theme, difficulty, use_llm)
    
    # 2. Generate matching dungeon levels for each region
    for region in world.get("regions", []):
        level = level_generator.generate_dungeon_grid(
            width=14 + difficulty,
            height=14 + difficulty,
            theme=theme,
            difficulty=difficulty,
        )
        level["name"] = region["name"]
        level_generator.export_level_json(level, name=f"{region['id']}_{theme}")
        region["level_file"] = f"{region['id']}_{theme}.json"
    
    # 3. Create custom texture pack for this world
    texture_packager.create_custom_texture_pack(theme, f"ai_world_{theme}")
    
    # 4. Save complete world manifest
    manifest_path = os.path.join(MYWORLD_DIR, f"manifest_{theme}_diff{difficulty}.json")
    with open(manifest_path, "w") as f:
        json.dump(world, f, indent=2)
    
    print(f"[Architect] World complete! Manifest: {manifest_path}")
    return world


def run_campaign(rounds=3, themes=None):
    """Run a multi-round campaign generating progressively harder worlds."""
    if not themes:
        themes = ["fantasy", "shadow", "ice", "fire", "sci-fi"]
    
    print(f"\n[Architect] Starting {rounds}-round campaign...")
    campaign_log = []
    
    for i in range(rounds):
        theme = themes[i % len(themes)]
        difficulty = 1 + i * 2
        print(f"\n--- Round {i+1}: {theme.upper()} (Difficulty {difficulty}) ---")
        
        world = build_world(theme, difficulty)
        campaign_log.append({
            "round": i + 1,
            "theme": theme,
            "difficulty": difficulty,
            "regions": len(world.get("regions", [])),
            "bosses": [b["name"] for b in world.get("bosses", [])],
            "manifest": f"manifest_{theme}_diff{difficulty}.json",
        })
    
    # Save campaign log
    log_path = os.path.join(MYWORLD_DIR, "campaign_log.json")
    with open(log_path, "w") as f:
        json.dump(campaign_log, f, indent=2)
    
    print(f"\n[Architect] Campaign complete! Log: {log_path}")
    return campaign_log


def catalog_everything():
    """Build complete catalogs: ROMs, textures, tools."""
    print("\n[Architect] Building complete asset catalog...")
    
    rom_count = len(rom_library.catalog_all_roms())
    tex_catalog = texture_packager.catalog_all_textures()
    
    summary = {
        "roms": rom_count,
        "textures": tex_catalog.get("total_textures", 0),
        "texture_packs": len(tex_catalog.get("texture_packs", [])),
        "texture_categories": list(tex_catalog.get("by_category", {}).keys()),
    }
    
    print(f"  ROMs: {summary['roms']}")
    print(f"  Textures: {summary['textures']}")
    print(f"  Texture Packs: {summary['texture_packs']}")
    print(f"  Categories: {', '.join(summary['texture_categories'])}")
    
    return summary


def scrape_new_assets():
    """Run live asset discovery."""
    print("\n[Architect] Discovering new assets online...")
    return asset_scraper.run_full_scrape()


def install_all_to_soh():
    """Install all available texture packs into Ship of Harkinian."""
    print("\n[Architect] Installing texture packs to SoH...")
    packs = ["OoT_Reloaded", "MM_Reloaded", "Classic64"]
    installed = []
    for pack in packs:
        result = texture_packager.install_texture_pack_to_soh(pack)
        if result:
            installed.append(pack)
    print(f"  Installed: {', '.join(installed)}")
    return installed


def swarm_generate(theme="fantasy", difficulty=3):
    """Submit world generation tasks to the SwarmCoordinator."""
    try:
        import requests
        coord = os.environ.get("SWARM_COORD", "http://localhost:7373")
        
        tasks = [
            ("dm_challenge", {"difficulty": difficulty}),
            ("generate_asset", {"type": "crystal", "theme": theme}),
            ("generate_asset", {"type": "tree", "theme": theme}),
            ("generate_asset", {"type": "terrain", "seed": random.randint(1, 999999)}),
            ("generate_asset", {"type": "dungeon_room", "theme": theme}),
        ]
        
        ids = []
        for ttype, payload in tasks:
            r = requests.post(f"{coord}/submit_task", json={
                "task_type": ttype,
                "payload": payload,
            }, timeout=10)
            tid = r.json().get("task_id")
            ids.append(tid)
            print(f"  Swarm task: {ttype} → #{tid}")
        
        return ids
    except Exception as e:
        print(f"[Architect] Swarm not available: {e}")
        return []


if __name__ == "__main__":
    print_banner()
    
    parser = argparse.ArgumentParser(description="N64 AI World Architect")
    parser.add_argument("--build", action="store_true", help="Build a complete world")
    parser.add_argument("--theme", default="fantasy", help="World theme")
    parser.add_argument("--difficulty", type=int, default=3, help="Difficulty 1-10")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM generation")
    parser.add_argument("--campaign", action="store_true", help="Run multi-round campaign")
    parser.add_argument("--rounds", type=int, default=3, help="Campaign rounds")
    parser.add_argument("--catalog", action="store_true", help="Catalog all assets")
    parser.add_argument("--scrape", action="store_true", help="Scrape for new assets")
    parser.add_argument("--install-soh", action="store_true", help="Install packs to SoH")
    parser.add_argument("--swarm", action="store_true", help="Distribute via swarm")
    args = parser.parse_args()
    
    if args.catalog:
        catalog_everything()
    elif args.scrape:
        scrape_new_assets()
    elif args.install_soh:
        install_all_to_soh()
    elif args.campaign:
        run_campaign(args.rounds)
    elif args.build:
        world = build_world(args.theme, args.difficulty, not args.no_llm)
        if args.swarm:
            swarm_generate(args.theme, args.difficulty)
    else:
        print("\nNo action specified. Try:")
        print("  --build --theme shadow --difficulty 5")
        print("  --campaign --rounds 5")
        print("  --catalog")
        print("  --install-soh")
