#!/usr/bin/env python3
"""
N64 AI Co-op Lab — Texture Packager
====================================
Packages texture assets into formats compatible with Ship of Harkinian.
Supports:
  - Copying PNG texture packs into SoH mods/ folder structure
  - Creating .o2r archives (if retro tool available)
  - Converting textures via n64texconv for homebrew use
  - Cataloging all available textures for AI selection
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

ASSETS_DIR = os.path.expanduser("~/HylianModding/Assets/Textures")
SOH_MODS_DIR = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods")
OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/texture_packs")
METADATA_DIR = os.path.expanduser("~/HylianModding/Library/Metadata")


def catalog_all_textures():
    """Index every texture file across all packs."""
    catalog = {
        "texture_packs": [],
        "total_textures": 0,
        "by_category": {},
    }
    
    for pack_dir in Path(ASSETS_DIR).iterdir():
        if not pack_dir.is_dir():
            continue
        
        textures = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tga"):
            for tex_file in pack_dir.rglob(ext):
                rel_path = str(tex_file.relative_to(pack_dir))
                category = guess_category(rel_path)
                textures.append({
                    "path": str(tex_file),
                    "relative": rel_path,
                    "category": category,
                    "size_kb": round(tex_file.stat().st_size / 1024, 2),
                })
        
        pack_info = {
            "name": pack_dir.name,
            "path": str(pack_dir),
            "texture_count": len(textures),
            "textures": textures[:500],  # Limit per pack to keep JSON manageable
        }
        catalog["texture_packs"].append(pack_info)
        catalog["total_textures"] += len(textures)
        
        for t in textures:
            cat = t["category"]
            if cat not in catalog["by_category"]:
                catalog["by_category"][cat] = []
            catalog["by_category"][cat].append({
                "pack": pack_dir.name,
                "path": t["relative"],
            })
    
    os.makedirs(METADATA_DIR, exist_ok=True)
    with open(os.path.join(METADATA_DIR, "texture_catalog.json"), "w") as f:
        json.dump(catalog, f, indent=2)
    
    return catalog


def guess_category(path):
    """Guess texture category from path/filename."""
    path_lower = path.lower()
    categories = {
        "dungeon": ["dungeon", "temple", "cave", "botw", "shadow", "spirit", "forest", "fire", "water", "ice"],
        "character": ["link", "zelda", "npc", "character", "goron", "zora", "kokiri", "gerudo"],
        "enemy": ["enemy", "boss", "moblin", "octorok", "stalfos", "wolfos"],
        "item": ["item", "weapon", "shield", "ocarina", "bomb", "arrow", "heart", "rupee"],
        "environment": ["grass", "ground", "wall", "sky", "cloud", "water", "lava", "tree", "rock"],
        "ui": ["icon", "hud", "menu", "font", "text"],
        "effect": ["flame", "ice", "magic", "particle", "sparkle"],
    }
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in path_lower:
                return cat
    return "misc"


def install_texture_pack_to_soh(pack_name, mod_name=None):
    """Copy a texture pack into SoH mods folder with proper structure."""
    if not mod_name:
        mod_name = f"ai_{pack_name.lower().replace(' ', '_')}"
    
    src_dir = os.path.join(ASSETS_DIR, pack_name)
    dst_dir = os.path.join(SOH_MODS_DIR, mod_name)
    
    if not os.path.exists(src_dir):
        print(f"[TexturePkg] Pack not found: {pack_name}")
        return None
    
    os.makedirs(dst_dir, exist_ok=True)
    
    # Copy PNGs into the mod directory
    copied = 0
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        for src_file in Path(src_dir).rglob(ext):
            rel = src_file.relative_to(src_dir)
            dst_file = Path(dst_dir) / rel
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1
    
    print(f"[TexturePkg] Installed {copied} textures to {dst_dir}")
    return dst_dir


def create_custom_texture_pack(theme, output_name=None):
    """Create a curated texture pack from multiple sources based on theme."""
    catalog_path = os.path.join(METADATA_DIR, "texture_catalog.json")
    if not os.path.exists(catalog_path):
        catalog = catalog_all_textures()
    else:
        with open(catalog_path) as f:
            catalog = json.load(f)
    
    if not output_name:
        output_name = f"ai_custom_{theme}"
    
    dst_dir = os.path.join(OUTPUT_DIR, output_name)
    os.makedirs(dst_dir, exist_ok=True)
    
    theme_keywords = {
        "fantasy": ["dungeon", "temple", "grass", "tree", "character", "item", "environment"],
        "sci-fi": ["metal", "tech", "sky", "environment"],
        "horror": ["dungeon", "shadow", "enemy", "environment"],
        "shadow": ["shadow", "dungeon", "dark", "enemy"],
        "ice": ["ice", "water", "dungeon", "environment"],
        "fire": ["fire", "lava", "dungeon", "environment"],
    }
    
    keywords = theme_keywords.get(theme, ["environment", "dungeon"])
    copied = 0
    
    for pack in catalog["texture_packs"]:
        for tex in pack.get("textures", []):
            if tex["category"] in keywords:
                src = tex["path"]
                dst = os.path.join(dst_dir, tex["relative"].replace("/", "_"))
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    copied += 1
                    if copied >= 1000:  # Limit pack size
                        break
        if copied >= 1000:
            break
    
    print(f"[TexturePkg] Created custom pack '{output_name}' with {copied} textures")
    return dst_dir


def package_as_o2r(source_dir, output_file):
    """Package textures into .o2r format (zip with specific structure)."""
    # For now, create a zip that SoH might recognize
    # True .o2r requires the retro tool or specific OTR format
    if not output_file.endswith(".o2r"):
        output_file += ".o2r"
    
    o2r_path = os.path.join(SOH_MODS_DIR, output_file)
    
    with zipfile.ZipFile(o2r_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)
    
    print(f"[TexturePkg] Packaged {o2r_path} ({os.path.getsize(o2r_path)//1024} KB)")
    return o2r_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", action="store_true", help="Build texture catalog")
    parser.add_argument("--install", help="Install pack to SoH mods")
    parser.add_argument("--create", help="Create themed custom pack")
    parser.add_argument("--package", help="Package directory as .o2r")
    args = parser.parse_args()
    
    if args.catalog:
        catalog_all_textures()
    elif args.install:
        install_texture_pack_to_soh(args.install)
    elif args.create:
        create_custom_texture_pack(args.create)
    elif args.package:
        package_as_o2r(args.package, os.path.basename(args.package) + ".o2r")
    else:
        print("Usage: texture_packager.py --catalog | --install <pack> | --create <theme> | --package <dir>")
