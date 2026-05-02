"""Run procedural generation inside Blender and export."""

import os
import sys
import json
import tempfile
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/blender")


def run_blender_export(mesh_dict: dict, name: str) -> dict:
    """Run Blender headlessly to create and export a mesh."""
    os.makedirs(BLEND_OUTPUT_DIR, exist_ok=True)

    blend_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}.blend")
    obj_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}.obj")

    # Write mesh data to temp JSON so Blender can read it
    mesh_json_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}_meshdata.json")
    with open(mesh_json_path, 'w') as f:
        json.dump(mesh_dict, f)

    script = f"""import sys
sys.path.insert(0, '{SCRIPT_DIR}')
import bpy
import json
from procedural_engine import MeshData, meshdata_to_blender, save_blend, export_obj

with open('{mesh_json_path}') as f:
    mesh_data = json.load(f)
mesh = MeshData(**mesh_data)
obj_name = meshdata_to_blender(mesh)
print(f"[Blender] Created object: {{obj_name}}")

save_blend('{blend_path}')
export_obj('{obj_path}')
print("[Blender] Export complete")
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ["blender", "--background", "--python", script_path],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0 and os.path.exists(blend_path)
    except Exception as e:
        output = str(e)
        success = False
    finally:
        os.unlink(script_path)
        if os.path.exists(mesh_json_path):
            os.unlink(mesh_json_path)

    return {
        "success": success,
        "blend": blend_path if os.path.exists(blend_path) else None,
        "obj": obj_path if os.path.exists(obj_path) else None,
        "output": output,
    }


if __name__ == "__main__":
    from procedural_engine import generate_crystal
    mesh = generate_crystal(seed=42)
    result = run_blender_export(mesh.__dict__, "test_crystal")
    print(json.dumps({k: v for k, v in result.items() if k != "output"}, indent=2))
