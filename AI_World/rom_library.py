#!/usr/bin/env python3
"""
N64 AI Co-op Lab — ROM Library Cataloger
=========================================
Scans the entire ROM library and catalogs every game with metadata.
Uses ROM headers to identify games, then cross-references with
known databases for genres, themes, and asset types.
"""

import os
import json
import struct
import hashlib
from pathlib import Path

ROM_DIR = os.path.expanduser("~/HylianModding/Library/ROMs")
METADATA_DIR = os.path.expanduser("~/HylianModding/Library/Metadata")

# Known game metadata mapping (title substring → metadata)
GAME_DB = {
    "Zelda": {"genre": "action-adventure", "themes": ["fantasy", "time", "dark"], "assets": ["dungeon", "overworld", "character"]},
    "Mario": {"genre": "platformer", "themes": ["colorful", "cartoon"], "assets": ["character", "level"]},
    "GoldenEye": {"genre": "fps", "themes": ["military", "stealth"], "assets": ["weapon", "character", "level"]},
    "Perfect Dark": {"genre": "fps", "themes": ["sci-fi", "cyberpunk"], "assets": ["weapon", "character", "level"]},
    "Star Fox": {"genre": "shooter", "themes": ["space", "sci-fi"], "assets": ["vehicle", "character"]},
    "Doom": {"genre": "fps", "themes": ["horror", "hell"], "assets": ["weapon", "monster", "level"]},
    "Quake": {"genre": "fps", "themes": ["gothic", "horror"], "assets": ["weapon", "monster", "level"]},
    "Banjo": {"genre": "platformer", "themes": ["cartoon", "collectathon"], "assets": ["character", "level"]},
    "Donkey Kong": {"genre": "platformer", "themes": ["jungle", "cartoon"], "assets": ["character", "level"]},
    "Pokemon": {"genre": "rpg", "themes": ["monster", "collection"], "assets": ["character", "creature", "level"]},
    "Paper Mario": {"genre": "rpg", "themes": ["paper", "fantasy"], "assets": ["character", "level"]},
    "Smash Bros": {"genre": "fighting", "themes": ["crossover", "arena"], "assets": ["character", "stage"]},
    "Kirby": {"genre": "platformer", "themes": ["cute", "dream"], "assets": ["character", "level"]},
    "F-Zero": {"genre": "racing", "themes": ["sci-fi", "speed"], "assets": ["vehicle", "track"]},
    "Mario Kart": {"genre": "racing", "themes": ["cartoon", "speed"], "assets": ["vehicle", "track", "character"]},
    "Harvest Moon": {"genre": "simulation", "themes": ["farm", "peaceful"], "assets": ["character", "building"]},
    "Castlevania": {"genre": "action", "themes": ["gothic", "horror"], "assets": ["character", "monster", "level"]},
    "Conker": {"genre": "platformer", "themes": ["mature", "comedy"], "assets": ["character", "level"]},
    "Body Harvest": {"genre": "action", "themes": ["sci-fi", "survival"], "assets": ["vehicle", "character", "level"]},
    "Jet Force": {"genre": "action", "themes": ["sci-fi", "shooter"], "assets": ["weapon", "character", "level"]},
    "Mystical Ninja": {"genre": "action", "themes": ["japan", "comedy"], "assets": ["character", "level"]},
    "Diddy Kong": {"genre": "racing", "themes": ["cartoon", "adventure"], "assets": ["vehicle", "character", "level"]},
    "Wave Race": {"genre": "racing", "themes": ["water", "sports"], "assets": ["vehicle", "track"]},
    "1080": {"genre": "sports", "themes": ["snow", "extreme"], "assets": ["character", "track"]},
    "Excitebike": {"genre": "racing", "themes": ["motorcycle", "extreme"], "assets": ["vehicle", "track"]},
    "Pilotwings": {"genre": "simulation", "themes": ["flight", "sports"], "assets": ["vehicle", "level"]},
    "Star Wars": {"genre": "action", "themes": ["sci-fi", "space"], "assets": ["vehicle", "character", "level"]},
    "Turok": {"genre": "fps", "themes": ["dinosaur", "jungle"], "assets": ["weapon", "monster", "level"]},
    "Resident Evil": {"genre": "survival-horror", "themes": ["zombie", "horror"], "assets": ["character", "monster", "level"]},
}


def read_rom_header(path):
    """Read basic ROM header info from .z64, .n64, or .v64 file."""
    with open(path, "rb") as f:
        raw = f.read(64)
    
    # Detect format
    if raw[0] == 0x80:
        # .z64 (big endian) or .n64 (little endian word swap)
        if raw[1] == 0x37:
            fmt = "z64"
            title = raw[0x20:0x34].decode("ascii", errors="ignore").strip()
            game_code = raw[0x3C:0x3E].decode("ascii", errors="ignore")
        else:
            fmt = "n64"
            # Would need byte swap - skip for now
            title = raw[0x20:0x34].decode("ascii", errors="ignore").strip()
            game_code = "???"
    elif raw[0] == 0x37:
        fmt = "v64"  # byte-swapped
        title = raw[0x20:0x34].decode("ascii", errors="ignore").strip()
        game_code = raw[0x3C:0x3E].decode("ascii", errors="ignore")
    else:
        fmt = "unknown"
        title = "Unknown"
        game_code = "???"
    
    return {
        "format": fmt,
        "title": title,
        "game_code": game_code,
        "size_bytes": os.path.getsize(path),
    }


def identify_game(title):
    """Cross-reference title with known game database."""
    for key, meta in GAME_DB.items():
        if key.lower() in title.lower():
            return meta
    return {"genre": "unknown", "themes": ["generic"], "assets": ["generic"]}


def catalog_all_roms():
    """Build complete catalog of all ROMs in library."""
    catalog = []
    rom_dir = Path(ROM_DIR)
    
    for rom_file in sorted(rom_dir.glob("*.*")):
        if rom_file.suffix.lower() not in (".z64", ".n64", ".v64"):
            continue
        
        try:
            header = read_rom_header(str(rom_file))
            meta = identify_game(header["title"])
            catalog.append({
                "filename": rom_file.name,
                "title": header["title"],
                "format": header["format"],
                "game_code": header["game_code"],
                "size_mb": round(header["size_bytes"] / (1024*1024), 2),
                **meta,
            })
        except Exception as e:
            catalog.append({
                "filename": rom_file.name,
                "title": "ERROR",
                "error": str(e),
            })
    
    os.makedirs(METADATA_DIR, exist_ok=True)
    with open(os.path.join(METADATA_DIR, "rom_catalog.json"), "w") as f:
        json.dump(catalog, f, indent=2)
    
    return catalog


def get_roms_by_theme(theme):
    """Return all ROMs matching a theme."""
    catalog_path = os.path.join(METADATA_DIR, "rom_catalog.json")
    if not os.path.exists(catalog_path):
        catalog = catalog_all_roms()
    else:
        with open(catalog_path) as f:
            catalog = json.load(f)
    
    return [r for r in catalog if theme.lower() in [t.lower() for t in r.get("themes", [])]]


def get_roms_by_genre(genre):
    """Return all ROMs matching a genre."""
    catalog_path = os.path.join(METADATA_DIR, "rom_catalog.json")
    if not os.path.exists(catalog_path):
        catalog = catalog_all_roms()
    else:
        with open(catalog_path) as f:
            catalog = json.load(f)
    
    return [r for r in catalog if genre.lower() == r.get("genre", "").lower()]


if __name__ == "__main__":
    catalog = catalog_all_roms()
    print(f"Cataloged {len(catalog)} ROMs")
    
    # Print summary by genre
    from collections import Counter
    genres = Counter(r.get("genre", "unknown") for r in catalog)
    print("\nBy genre:")
    for g, c in genres.most_common():
        print(f"  {g}: {c}")
