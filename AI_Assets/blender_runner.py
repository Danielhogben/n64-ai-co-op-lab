"""Run procedural generation inside Blender and export."""

import os
import sys
import json
import tempfile
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_OUTPUT_DIR = os.path.expanduser("~/HylianModding/MyWorld/blender")


def _blender_script_template(mesh_json: str, blend_path: str, obj_path: str, fbx_path: str) -> str:
    return f"""import sys
sys.path.insert(0, '{SCRIPT_DIR}')
import bpy
from procedural_engine import MeshData, meshdata_to_blender, save_blend, export_obj, export_fbx

mesh_data = {mesh_json}
mesh = MeshData(**mesh_data)
name = meshdata_to_blender(mesh)
print(f"[Blender] Created object: {{name}}")

save_blend('{blend_path}')
export_obj('{obj_path}')
# export_fbx('{fbx_path}')

print("[Blender] Export complete")
"""


def run_blender_export(mesh_dict: dict, name: str) -> dict:
    """Run Blender headlessly to create and export a mesh."""
    os.makedirs(BLEND_OUTPUT_DIR, exist_ok=True)

    blend_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}.blend")
    obj_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}.obj")
    fbx_path = os.path.join(BLEND_OUTPUT_DIR, f"{name}.fbx")

    mesh_json = json.dumps(mesh_dict)
    script = _blender_script_template(mesh_json, blend_path, obj_path, fbx_path)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ["blender", "--background", "--python", script_path],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
    except Exception as e:
        output = str(e)
        success = False
    finally:
        os.unlink(script_path)

    return {
        "success": success,
        "blend": blend_path if success and os.path.exists(blend_path) else None,
        "obj": obj_path if success and os.path.exists(obj_path) else None,
        "fbx": fbx_path if success and os.path.exists(fbx_path) else None,
        "output": output,
    }


if __name__ == "__main__":
    # Test
    from procedural_engine import generate_crystal
    mesh = generate_crystal(seed=42)
    result = run_blender_export(mesh.__dict__, "test_crystal")
    print(json.dumps(result, indent=2))
