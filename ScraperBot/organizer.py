#!/usr/bin/env python3
"""
N64 Asset Organizer
====================
Scans downloaded assets and organizes them into categorized directories.
Generates a master catalog with metadata.
"""

import os
import json
import shutil
from pathlib import Path
from collections import defaultdict

DOWNLOAD_DIR = os.path.expanduser("~/HylianModding/Assets/Downloads")
ASSETS_DIR = os.path.expanduser("~/HylianModding/Assets")
CATALOG_PATH = os.path.expanduser("~/HylianModding/ScraperBot/outputs/asset_catalog.json")

# File type categories
CATEGORIES = {
    "tools": [".exe", ".py", ".js", ".sh", ".bat", ".zip", ".7z", ".tar.gz", ".tar.xz", ".deb", ".rpm"],
    "textures": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga", ".dds"],
    "models": [".obj", ".fbx", ".dae", ".3ds", ".blend", ".glb", ".gltf"],
    "audio": [".wav", ".mp3", ".ogg", ".flac", ".mid", ".midi"],
    "docs": [".txt", ".md", ".pdf", ".doc", ".docx"],
    "roms": [".n64", ".z64", ".v64", ".rom"],
    "code": [".c", ".cpp", ".h", ".s", ".asm", ".json", ".xml", ".yaml", ".yml"],
}

def get_category(filename: str) -> str:
    """Determine file category based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "other"


def scan_directory(base_dir: str) -> dict:
    """Scan directory and categorize files."""
    catalog = {
        "total_files": 0,
        "total_size": 0,
        "by_category": defaultdict(list),
        "by_source": defaultdict(list),
        "files": [],
    }

    for root, dirs, files in os.walk(base_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if not os.path.isfile(fpath):
                continue

            size = os.path.getsize(fpath)
            category = get_category(fname)
            rel_path = os.path.relpath(fpath, base_dir)

            # Determine source from path
            parts = rel_path.split(os.sep)
            source = parts[0] if len(parts) > 1 else "unknown"

            entry = {
                "name": fname,
                "path": rel_path,
                "size": size,
                "category": category,
                "source": source,
            }

            catalog["files"].append(entry)
            catalog["by_category"][category].append(entry)
            catalog["by_source"][source].append(entry)
            catalog["total_files"] += 1
            catalog["total_size"] += size

    # Convert defaultdicts to regular dicts
    catalog["by_category"] = dict(catalog["by_category"])
    catalog["by_source"] = dict(catalog["by_source"])

    return catalog


def organize_files(catalog: dict, dest_dir: str):
    """Organize files into categorized directories."""
    os.makedirs(dest_dir, exist_ok=True)

    for entry in catalog["files"]:
        src = os.path.join(DOWNLOAD_DIR, entry["path"])
        if not os.path.exists(src):
            continue

        # Destination: categorized by source then type
        dest = os.path.join(dest_dir, entry["source"], entry["category"], entry["name"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        try:
            shutil.copy2(src, dest)
        except Exception as e:
            print(f"Error copying {src}: {e}")


def print_summary(catalog: dict):
    """Print catalog summary."""
    print(f"\n=== Asset Catalog Summary ===")
    print(f"Total files: {catalog['total_files']}")
    print(f"Total size: {catalog['total_size'] / 1024 / 1024:.2f} MB")

    print(f"\nBy Category:")
    for cat, entries in sorted(catalog["by_category"].items()):
        total = sum(e["size"] for e in entries)
        print(f"  {cat}: {len(entries)} files ({total / 1024 / 1024:.2f} MB)")

    print(f"\nBy Source:")
    for src, entries in sorted(catalog["by_source"].items()):
        total = sum(e["size"] for e in entries)
        print(f"  {src}: {len(entries)} files ({total / 1024 / 1024:.2f} MB)")


def main():
    print(f"[Organizer] Scanning {DOWNLOAD_DIR}...")
    catalog = scan_directory(DOWNLOAD_DIR)
    print_summary(catalog)

    # Save catalog
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    with open(CATALOG_PATH, 'w') as f:
        json.dump(catalog, f, indent=2)
    print(f"\n[Organizer] Catalog saved to: {CATALOG_PATH}")

    # Organize into Assets directory
    organized_dir = os.path.join(ASSETS_DIR, "Organized")
    print(f"\n[Organizer] Organizing files to {organized_dir}...")
    organize_files(catalog, organized_dir)
    print(f"[Organizer] Done!")


if __name__ == "__main__":
    main()
