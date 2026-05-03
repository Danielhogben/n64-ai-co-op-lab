import bpy
import sys
import os
import random

def setup_fast64():
    """Enable Fast64 addon in Blender."""
    try:
        bpy.ops.preferences.addon_enable(module='fast64')
        print("[AI] Fast64 enabled.")
    except Exception as e:
        print(f"[AI] Fast64 enable failed: {e}")

def create_n64_mesh(mesh_type="cube", name="AI_Object"):
    """Create a basic N64-compatible mesh."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    if mesh_type == "cube":
        bpy.ops.mesh.primitive_cube_add()
    elif mesh_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add()
    
    obj = bpy.context.active_object
    obj.name = name
    
    # Set N64 material properties via Fast64 if enabled
    if hasattr(bpy.types, "FAST64_MT_material_settings"):
        print(f"[AI] Applying Fast64 N64 settings to {name}")
        # Custom Fast64 logic would go here
        
    return obj

if __name__ == "__main__":
    setup_fast64()
    create_n64_mesh(mesh_type=sys.argv[-1] if len(sys.argv) > 1 else "cube")
    bpy.ops.wm.save_as_mainfile(filepath="/tmp/ai_n64_model.blend")
