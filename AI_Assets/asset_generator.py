"""Main orchestrator: LLM plans, engine builds, Blender exports."""

import os
import sys
import json
import argparse
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from asset_analyzer import get_catalog_summary, load_catalog
from procedural_engine import (
    generate_terrain, generate_crystal, generate_tree,
    generate_dungeon_room, generate_spike_trap, generate_biome,
)
from blender_runner import run_blender_export


def get_llm():
    from llm_generator import AssetLLM
    return AssetLLM()


def generate_asset_cli(asset_type: str, theme: str, seed: int = 42,
                       use_llm: bool = False, output_dir: str = None) -> str:
    """Generate an asset and return the path to the saved file."""
    if output_dir is None:
        output_dir = os.path.expanduser("~/HylianModding/MyWorld/blender")
    os.makedirs(output_dir, exist_ok=True)

    print(f"[Generator] Type={asset_type}, Theme={theme}, Seed={seed}")

    # Use LLM if requested
    if use_llm:
        try:
            llm = get_llm()
            prompt = f"Generate a {theme} themed {asset_type} for Ocarina of Time N64. Low poly."
            result = llm.generate_asset_script(prompt)
            script_content = result.get("python_script", "")
            print(f"[LLM] Generated: {result.get('name', 'Unknown')}")
            print(f"[LLM] Description: {result.get('description', '')[:100]}...")
        except Exception as e:
            print(f"[LLM] Failed ({e}), falling back to procedural engine")

    # Build the asset
    if asset_type == "terrain":
        mesh = generate_terrain(size=48, scale=0.1, height=3.0, seed=seed)
    elif asset_type == "crystal":
        mesh = generate_crystal(radius=1.0, height=2.5, segments=6, seed=seed)
    elif asset_type == "tree":
        mesh = generate_tree(trunk_height=2.5, foliage_radius=1.5, seed=seed)
    elif asset_type == "dungeon_room":
        mesh = generate_dungeon_room(width=12, depth=12, height=5, seed=seed)
    elif asset_type == "spike_trap":
        mesh = generate_spike_trap(count=5, seed=seed)
    elif asset_type == "biome":
        meshes = generate_biome(biome_type=theme, count=10, seed=seed)
        # For biome, export the first mesh as representative
        mesh = meshes[0] if meshes else None
        # TODO: export all meshes in the biome
    else:
        mesh = generate_crystal(seed=seed)

    if mesh is None:
        return ""

    name = f"{mesh.name}_{theme}_{seed}"
    result = run_blender_export(mesh.__dict__, name)

    if result.get("blend"):
        print(f"[Generator] Exported blend: {result['blend']}")
    if result.get("obj"):
        print(f"[Generator] Exported obj: {result['obj']}")

    if not result.get("blend"):
        # Fallback: save raw JSON
        json_path = os.path.join(output_dir, f"{name}.json")
        with open(json_path, 'w') as f:
            json.dump(mesh.__dict__, f, indent=2)
        print(f"[Generator] Saved JSON fallback: {json_path}")
        return json_path

    return result.get("blend", "")


def main():
    parser = argparse.ArgumentParser(description="AI Procedural Asset Generator")
    parser.add_argument("--type", default="crystal", help="Asset type: terrain|crystal|tree|dungeon_room|spike_trap|biome")
    parser.add_argument("--theme", default="forest", help="Theme: forest|crystal_cave|dungeon|fire|ice|shadow")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--llm", action="store_true", help="Use LLM for creative generation")
    parser.add_argument("--catalog", action="store_true", help="Print model catalog summary")
    parser.add_argument("--output", default=None, help="Output directory")
    args = parser.parse_args()

    if args.catalog:
        print(get_catalog_summary())
        return

    path = generate_asset_cli(
        asset_type=args.type,
        theme=args.theme,
        seed=args.seed,
        use_llm=args.llm,
        output_dir=args.output
    )
    if path:
        print(f"[Done] Asset saved to: {path}")


if __name__ == "__main__":
    main()
