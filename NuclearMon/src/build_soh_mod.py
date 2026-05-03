#!/usr/bin/env python3
"""
NuclearMon — Ship of Harkinian Mod Builder
Packages the wasteland texture pack and mod metadata for SoH.
"""

import os
import json
import shutil

NUCLEAR_MON_DIR = os.path.expanduser("~/HylianModding/NuclearMon")
SOH_MODS_DIR = os.path.expanduser("~/HylianModding/ShipOfHarkinian/mods")
CLASSIC64_BASE = "/home/donn/Downloads"

# Wasteland-relevant texture keywords and categories
WASTELAND_CATEGORIES = {
    "ground": ["ground", "dirt", "mud", "ash", "sand", "soil"],
    "industrial": ["industrial", "factory", "metal", "rust", "pipe"],
    "concrete": ["concrete", "cement", "pavement", "road"],
    "rocks": ["rock", "stone", "gravel", "rubble"],
    "ruins": ["brick", "wall", "broken", "ruin", "debris"],
    "metal": ["metal", "steel", "iron", "plate", "grate"],
    "nature_dead": ["dead", "withered", "dry", "brown_grass"],
    "water_toxic": ["water", "sludge", "toxic", "green_water"],
}


def find_classic64_textures():
    """Find all Classic64 textures across all versions."""
    textures = []
    for version in ["0.3", "0.4", "0.5", "0.6"]:
        base = f"/home/donn/Downloads/- Classic 64 Asset Pack {version}"
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tga")):
                    textures.append({
                        "path": os.path.join(root, f),
                        "name": f,
                        "version": version,
                        "category": os.path.basename(root),
                    })
    return textures


def score_texture_for_wasteland(tex):
    """Score how well a texture fits the wasteland theme."""
    name = tex["name"].lower()
    cat = tex["category"].lower()
    score = 0
    for category, keywords in WASTELAND_CATEGORIES.items():
        for kw in keywords:
            if kw in name or kw in cat:
                score += 1
    # Boost certain categories
    if "industrial" in cat or "metal" in cat or "concrete" in cat:
        score += 2
    if "ground" in cat or "rocks" in cat:
        score += 1
    return score


def build_soh_mod():
    """Build and install the NuclearMon SoH mod."""
    mod_name = "nuclearmon_wasteland"
    mod_dir = os.path.join(SOH_MODS_DIR, mod_name)
    os.makedirs(mod_dir, exist_ok=True)

    print(f"[NuclearMon] Building SoH mod: {mod_name}")

    # Find and score textures
    all_textures = find_classic64_textures()
    print(f"[NuclearMon] Found {len(all_textures)} Classic64 textures")

    scored = [(t, score_texture_for_wasteland(t)) for t in all_textures]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take top-scoring textures
    selected = [t for t, s in scored if s > 0][:500]  # Limit to 500
    print(f"[NuclearMon] Selected {len(selected)} wasteland textures")

    # Copy textures to mod dir
    for tex in selected:
        dest = os.path.join(mod_dir, tex["name"])
        shutil.copy2(tex["path"], dest)

    # Create mod manifest
    manifest = {
        "name": mod_name,
        "display_name": "NuclearMon: Wasteland",
        "description": "Post-apocalyptic Pokémon wasteland textures for Ship of Harkinian. Muddy browns, industrial grays, toxic greens.",
        "author": "NuclearMon Team",
        "version": "0.1.0",
        "texture_count": len(selected),
        "game": "NuclearMon",
    }
    with open(os.path.join(mod_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[NuclearMon] SoH mod installed to: {mod_dir}")
    print(f"[NuclearMon] Toggle in-game with Tab (Graphics → Mods → Alternate Assets)")
    return mod_dir


def build_o2r_pack():
    """Build a .o2r package (zipped mod) for distribution."""
    import zipfile

    mod_name = "nuclearmon_wasteland"
    mod_dir = os.path.join(SOH_MODS_DIR, mod_name)
    o2r_path = os.path.join(NUCLEAR_MON_DIR, "builds", f"{mod_name}.o2r")
    os.makedirs(os.path.dirname(o2r_path), exist_ok=True)

    with zipfile.ZipFile(o2r_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(mod_dir):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, mod_dir)
                zf.write(full, arc)

    print(f"[NuclearMon] .o2r pack built: {o2r_path}")
    return o2r_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install to SoH mods/")
    parser.add_argument("--pack", action="store_true", help="Build .o2r distribution pack")
    args = parser.parse_args()

    if args.install or not args.pack:
        build_soh_mod()
    if args.pack:
        build_o2r_pack()
