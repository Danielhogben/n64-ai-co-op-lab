"""Local LLM integration for procedural asset generation."""

import os
import json
from typing import Optional

from llama_cpp import Llama

# Pick a coding model from the user's collection
# Default to smallest/fastest for responsiveness
DEFAULT_MODEL = os.path.expanduser("~/Downloads/models/coding/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
# Fallbacks in order of preference
FALLBACK_MODELS = [
    os.path.expanduser("~/Downloads/models/coding/qwen2.5-coder-0.5b-instruct-q4_k_m.gguf"),
    os.path.expanduser("~/Downloads/models/coding/qwen2.5-coder-3b-instruct-q4_k_m.gguf"),
    os.path.expanduser("~/Downloads/models/coding/qwen2.5-coder-7b-instruct-q4_k_m.gguf"),
    os.path.expanduser("~/Downloads/models/hermes/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf"),
    os.path.expanduser("~/Downloads/models/core/Phi-3.5-mini-instruct-Q4_K_M.gguf"),
]

SYSTEM_PROMPT = """You are an expert N64 game asset designer and Python programmer.
Your task is to generate creative, procedurally-generated 3D assets for The Legend of Zelda: Ocarina of Time.

Constraints:
- N64 uses very low polygon counts (target 200-800 triangles for objects, 1000-3000 for scenes)
- Textures are small (32x32, 64x64 pixels typical)
- Colors use the N64 color combiner (simple diffuse + environment mapping)
- Output valid Python code that uses bpy (Blender Python API) to create meshes
- The code must be self-contained and runnable with `blender --background --python script.py`
- Use only built-in Python libraries + bpy

When generating:
1. Give the asset a creative name and lore description
2. Provide the complete Python generation script
3. Explain the design choices

Asset types you can generate:
- dungeon_rooms: enclosed spaces with walls, floors, pillars, doors
- terrain: heightmapped ground with rocks, grass patches
- structures: temples, houses, towers, bridges
- items: swords, shields, keys, magical artifacts
- enemies: stylized low-poly creatures
- vegetation: trees, bushes, flowers
- crystals/gems: glowing geometric shapes
- traps: spike pits, flame jets, crushing blocks
"""


class AssetLLM:
    def __init__(self, model_path: Optional[str] = None, n_ctx: int = 8192, n_threads: Optional[int] = None):
        self.model_path = model_path or self._find_model()
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"No GGUF model found. Tried: {self.model_path}")

        print(f"[LLM] Loading model: {os.path.basename(self.model_path)}")
        self.n_threads = n_threads or os.cpu_count()

        # Try GPU offload if CUDA is available, else CPU
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=self.n_threads,
                n_batch=512,
                verbose=False,
                n_gpu_layers=-1,  # Auto-detect GPU layers
            )
            print(f"[LLM] Model loaded (GPU offload attempted)")
        except Exception as e:
            print(f"[LLM] GPU offload failed ({e}), falling back to CPU")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=self.n_threads,
                n_batch=512,
                verbose=False,
                n_gpu_layers=0,
            )
            print(f"[LLM] Model loaded (CPU)")

    def _find_model(self) -> str:
        for path in [DEFAULT_MODEL] + FALLBACK_MODELS:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("No GGUF model found in ~/Downloads/models/")

    def generate_asset_script(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.75) -> dict:
        """Generate a Python Blender script for a procedural asset."""
        full_prompt = f"""{SYSTEM_PROMPT}

Generate a procedural asset based on this request: {prompt}

Respond in JSON format:
{{
  "name": "AssetName",
  "description": "Lore description of the asset",
  "category": "dungeon_room|terrain|structure|item|enemy|vegetation|crystal|trap",
  "python_script": "complete self-contained bpy script as a string",
  "poly_count_estimate": 500,
  "design_notes": "explanation of design choices"
}}

JSON response:"""

        output = self.llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["}\n```", "}\n\n", "</s>"],
        )
        text = output["choices"][0]["text"].strip()

        # Try to extract JSON
        try:
            # Sometimes the model wraps in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            result = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: return raw text
            result = {
                "name": "GeneratedAsset",
                "description": prompt,
                "category": "misc",
                "python_script": text,
                "poly_count_estimate": 500,
                "design_notes": "Raw output (JSON parse failed)",
            }

        return result

    def generate_terrain_description(self, theme: str = "forest") -> dict:
        """Generate terrain parameters for the procedural engine."""
        prompt = f"Generate terrain parameters for a {theme} biome. Include heightmap noise settings, color palette, and feature placements."
        return self.generate_asset_script(prompt, max_tokens=1024)

    def generate_dungeon_room(self, theme: str = "fire", difficulty: int = 5) -> dict:
        """Generate a dungeon room layout."""
        prompt = f"Generate a {theme} themed dungeon room for difficulty {difficulty}/10. Include trap placements, enemy spawn points, and puzzle elements."
        return self.generate_asset_script(prompt, max_tokens=2048)

    def generate_item(self, item_type: str = "magical_artifact", rarity: str = "rare") -> dict:
        """Generate an item model."""
        prompt = f"Generate a {rarity} {item_type} item for Ocarina of Time. It should look iconic and fit the Zelda art style."
        return self.generate_asset_script(prompt, max_tokens=1536)


if __name__ == "__main__":
    print("Testing LLM generator...")
    gen = AssetLLM()
    result = gen.generate_item(item_type="crystal_sword", rarity="legendary")
    print(json.dumps(result, indent=2))
