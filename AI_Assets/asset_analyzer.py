"""Analyze existing N64 assets (.zobj files) to build a knowledge base."""

import os
import json
from pathlib import Path
from typing import Dict, List

ZOBJ_DIR = os.path.expanduser("~/HylianModding/Tools/SharpOcarina/F3DEX2")
CATALOG_PATH = os.path.expanduser("~/HylianModding/AI_Assets/model_catalog.json")

# Category mapping based on filename patterns
CATEGORY_PATTERNS = {
    "link": ["link", "adultlink", "childlink"],
    "enemy": ["stalfos", "keese", "octorok", "wolfos", "lizalfos", "dodongo", "tektite",
              "peahat", "skulltula", "stalfo", "bubble", "wallmaster", "floormaster",
              "redead", "gibdo", "iron_knuckle", "freezard", "dark_link", "ganon",
              "deku", "baba", "okuta", "anubice", "bigokuta", "bji", "bl", "bob", "boj",
              "bombf", "bombiwa", "bowl", "brob", "bv", "bw", "bwall", "bxa", "b_heart",
              "cne", "cob", "cow", "crow", "cs", "daiku", "dekubaba", "dekujr", "dekunuts",
              "demo_6k", "ddan", "bdoor", "bg", "bird", "blkobj", "bl", "boji", "bubble",
              "bwall", "bji", "ane", "ani", "am", "ahg", "aob", "bba", "bb", "bji"],
    "npc": ["npc", "shop", "soldier", "guard", "sage", "fairy", "navi", "saria", "malon",
            "ruto", "zelda", "impa", "sheik", "goron", "gerudo", "kokiri", "hylians",
            "object_cow", "object_cs", "object_daiku", "object_bob", "object_boj",
            "object_ahg", "object_ane", "object_ani", "object_am", "object_aob", "object_cne", "object_cob"],
    "item": ["sword", "shield", "bow", "arrow", "bomb", "rupee", "heart", "key", "compass",
             "map", "ocarina", "hookshot", "hammer", "lens", "boomerang", "nut", "stick",
             "bean", "letter", "potion", "bottle", "mask", "medallion", "stone", "tunic",
             "boots", "gauntlet", "scale"],
    "environment": ["tree", "rock", "grass", "flower", "bush", "water", "lava", "ice",
                    "sky", "cloud", "fog", "snow", "sand", "dirt", "brick", "wall", "floor",
                    "door", "chest", "sign", "torch", "ladder", "bridge", "fence", "pillar",
                    "statue", "altar", "platform", "elevator", "switch", "crate", "barrel",
                    "pot", "skull", "bone", "web", "cobweb", "field", "dungeon", "temple"],
    "vehicle": ["horse", "epona", "boat", "raft", "cart"],
    "ui": ["font", "text", "icon", "cursor", "menu", "hud"],
    "effect": ["flame", "fire", "smoke", "spark", "magic", "light", "glow", "particle",
               "explosion", "beam", "wave", "ripple", "bubble", "steam"],
    "building": ["house", "shop", "tent", "castle", "tower", "temple", "cave", "well",
                 "stable", "market", "bridge", "gate", "arch", "room"],
}


def categorize_name(name: str) -> List[str]:
    """Guess categories from filename."""
    lowered = name.lower()
    categories = []
    for cat, patterns in CATEGORY_PATTERNS.items():
        if any(p in lowered for p in patterns):
            categories.append(cat)
    if not categories:
        categories.append("misc")
    return categories


def analyze_zobj_directory(zobj_dir: str = ZOBJ_DIR) -> Dict:
    """Scan all .zobj files and build a catalog."""
    catalog = {
        "total_files": 0,
        "total_bytes": 0,
        "categories": {},
        "files": [],
    }

    for f in sorted(Path(zobj_dir).glob("*.zobj")):
        size = f.stat().st_size
        name = f.stem
        cats = categorize_name(name)

        entry = {
            "name": name,
            "size": size,
            "path": str(f.relative_to(zobj_dir)),
            "categories": cats,
        }
        catalog["files"].append(entry)
        catalog["total_files"] += 1
        catalog["total_bytes"] += size

        for cat in cats:
            if cat not in catalog["categories"]:
                catalog["categories"][cat] = {"count": 0, "total_size": 0, "files": []}
            catalog["categories"][cat]["count"] += 1
            catalog["categories"][cat]["total_size"] += size
            catalog["categories"][cat]["files"].append(name)

    return catalog


def save_catalog(catalog: Dict, path: str = CATALOG_PATH):
    with open(path, 'w') as f:
        json.dump(catalog, f, indent=2)
    print(f"[Analyzer] Catalog saved to {path}")
    print(f"[Analyzer] Total models: {catalog['total_files']}")
    print(f"[Analyzer] Total size: {catalog['total_bytes']:,} bytes")
    for cat, info in sorted(catalog['categories'].items(), key=lambda x: -x[1]['count']):
        print(f"  {cat}: {info['count']} files ({info['total_size']:,} bytes)")


def load_catalog(path: str = CATALOG_PATH) -> Dict:
    with open(path) as f:
        return json.load(f)


def get_catalog_summary(catalog: Dict = None, max_items: int = 50) -> str:
    """Generate a text summary for the LLM context."""
    if catalog is None:
        catalog = load_catalog()

    lines = [
        f"N64 Asset Library Summary:",
        f"- Total models: {catalog['total_files']}",
        f"- Categories: {len(catalog['categories'])}",
        "",
        "Categories breakdown:",
    ]
    for cat, info in sorted(catalog['categories'].items(), key=lambda x: -x[1]['count']):
        files = info['files'][:max_items]
        lines.append(f"  [{cat}] {info['count']} models: {', '.join(files)}")
    lines.append("")
    lines.append("Use these as inspiration for procedural generation. N64 constraints: low poly (~500-2000 tris), small textures (32x32 to 64x64), simple materials.")
    return "\n".join(lines)


if __name__ == "__main__":
    catalog = analyze_zobj_directory()
    save_catalog(catalog)
    print("\n" + get_catalog_summary(catalog, max_items=20))
