"""Procedural generation engine for N64-compatible 3D assets.

Generates meshes using pure Python + math, then exports via Blender's bpy.
No GUI required — runs headless.
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    import bpy
    import bmesh
    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False

try:
    import noise
    HAS_NOISE = True
except ImportError:
    HAS_NOISE = False


@dataclass
class MeshData:
    """Simple mesh representation before Blender import."""
    vertices: List[Tuple[float, float, float]]
    faces: List[Tuple[int, ...]]
    uvs: Optional[List[Tuple[float, float]]] = None
    name: str = "procedural_mesh"


# ---------------------------------------------------------------------------
# CORE GENERATORS
# ---------------------------------------------------------------------------

def generate_terrain(size: int = 32, scale: float = 0.1, height: float = 3.0,
                     seed: int = 42, octaves: int = 4) -> MeshData:
    """Generate a heightmap terrain mesh."""
    if not HAS_NOISE:
        # Fallback: sine-based terrain
        verts = []
        faces = []
        for z in range(size):
            for x in range(size):
                y = math.sin(x * scale) * math.cos(z * scale) * height
                verts.append((x - size/2, y, z - size/2))
        for z in range(size - 1):
            for x in range(size - 1):
                i = z * size + x
                faces.append((i, i + 1, i + size + 1, i + size))
        return MeshData(vertices=verts, faces=faces, name="sine_terrain")

    random.seed(seed)
    verts = []
    faces = []
    for z in range(size):
        for x in range(size):
            nx = x * scale
            nz = z * scale
            y = noise.pnoise2(nx, nz, octaves=octaves, persistence=0.5, lacunarity=2.0,
                              repeatx=1024, repeaty=1024, base=seed) * height
            y = max(0, y)  # Clamp below water
            verts.append((x - size/2, y, z - size/2))

    for z in range(size - 1):
        for x in range(size - 1):
            i = z * size + x
            faces.append((i, i + 1, i + size + 1, i + size))

    return MeshData(vertices=verts, faces=faces, name="noise_terrain")


def generate_crystal(radius: float = 1.0, height: float = 2.0, segments: int = 6,
                     spikes: int = 3, seed: int = 42) -> MeshData:
    """Generate a low-poly crystal / gem."""
    random.seed(seed)
    verts = [(0, height, 0)]  # Top point

    # Bottom center
    verts.append((0, 0, 0))

    # Ring vertices
    for i in range(segments):
        angle = (i / segments) * math.tau
        r = radius * (1.0 + random.uniform(-0.1, 0.1))
        x = math.cos(angle) * r
        z = math.sin(angle) * r
        y = height * 0.3 + random.uniform(0, height * 0.2)
        verts.append((x, y, z))

    faces = []
    # Top faces (triangles to top point)
    for i in range(segments):
        next_i = (i + 1) % segments + 2
        curr_i = i + 2
        faces.append((0, next_i, curr_i))

    # Bottom faces (triangles to bottom center)
    for i in range(segments):
        next_i = (i + 1) % segments + 2
        curr_i = i + 2
        faces.append((1, curr_i, next_i))

    return MeshData(vertices=verts, faces=faces, name="crystal")


def generate_tree(trunk_height: float = 2.0, trunk_radius: float = 0.2,
                  foliage_radius: float = 1.0, foliage_levels: int = 3,
                  seed: int = 42) -> MeshData:
    """Generate a stylized low-poly tree."""
    random.seed(seed)
    verts = []
    faces = []

    # Trunk (cylinder-ish, low poly)
    trunk_segments = 5
    for y_level in [0, trunk_height]:
        for i in range(trunk_segments):
            angle = (i / trunk_segments) * math.tau
            r = trunk_radius * (0.8 if y_level > 0 else 1.0)
            x = math.cos(angle) * r
            z = math.sin(angle) * r
            verts.append((x, y_level, z))

    # Trunk faces
    for i in range(trunk_segments):
        next_i = (i + 1) % trunk_segments
        faces.append((i, next_i, next_i + trunk_segments, i + trunk_segments))

    offset = len(verts)

    # Foliage (stacked cones)
    for level in range(foliage_levels):
        level_y = trunk_height + level * (foliage_radius * 0.8)
        level_r = foliage_radius * (1.0 - level / foliage_levels)
        level_segments = max(5, int(level_r * 8))

        # Base ring
        for i in range(level_segments):
            angle = (i / level_segments) * math.tau
            x = math.cos(angle) * level_r
            z = math.sin(angle) * level_r
            verts.append((x, level_y, z))

        # Tip
        tip_idx = len(verts)
        verts.append((0, level_y + level_r * 1.2, 0))

        for i in range(level_segments):
            next_i = (i + 1) % level_segments + offset
            curr_i = i + offset
            faces.append((tip_idx, next_i, curr_i))

        offset += level_segments + 1

    return MeshData(vertices=verts, faces=faces, name="tree")


def generate_dungeon_room(width: float = 10.0, depth: float = 10.0, height: float = 4.0,
                          pillars: int = 4, torch_count: int = 4, seed: int = 42) -> MeshData:
    """Generate a simple dungeon room with floor, walls, pillars."""
    random.seed(seed)
    verts = []
    faces = []

    # Floor
    fw, fd = width, depth
    verts.extend([
        (-fw/2, 0, -fd/2), (fw/2, 0, -fd/2),
        (fw/2, 0, fd/2), (-fw/2, 0, fd/2)
    ])
    faces.append((0, 1, 2, 3))

    # Ceiling
    verts.extend([
        (-fw/2, height, -fd/2), (fw/2, height, -fd/2),
        (fw/2, height, fd/2), (-fw/2, height, fd/2)
    ])
    faces.append((4, 7, 6, 5))

    # Walls (4 walls, each as 2 triangles)
    wall_offset = len(verts)
    # We'll reuse floor/ceiling corners for walls
    # Back wall
    faces.append((0, 3, 7, 4))
    # Front wall
    faces.append((1, 5, 6, 2))
    # Left wall
    faces.append((0, 4, 5, 1))
    # Right wall
    faces.append((3, 2, 6, 7))

    # Pillars
    for i in range(pillars):
        px = random.uniform(-fw/2 + 1, fw/2 - 1)
        pz = random.uniform(-fd/2 + 1, fd/2 - 1)
        pr = 0.3
        p_base = len(verts)
        for y_level in [0, height]:
            for j in range(4):
                angle = (j / 4) * math.tau + math.pi/4
                x = px + math.cos(angle) * pr
                z = pz + math.sin(angle) * pr
                verts.append((x, y_level, z))
        for j in range(4):
            next_j = (j + 1) % 4
            faces.append((p_base + j, p_base + next_j,
                          p_base + next_j + 4, p_base + j + 4))

    return MeshData(vertices=verts, faces=faces, name="dungeon_room")


def generate_spike_trap(count: int = 5, base_size: float = 0.5, height: float = 1.5,
                        spacing: float = 1.0) -> MeshData:
    """Generate a row of floor spikes."""
    verts = []
    faces = []

    for i in range(count):
        x = i * spacing
        base = len(verts)
        # Base square
        s = base_size / 2
        verts.extend([
            (x - s, 0, -s), (x + s, 0, -s),
            (x + s, 0, s), (x - s, 0, s),
            (x, height, 0)  # Tip
        ])
        # 4 faces per spike
        faces.extend([
            (base + 0, base + 1, base + 4),
            (base + 1, base + 2, base + 4),
            (base + 2, base + 3, base + 4),
            (base + 3, base + 0, base + 4),
            (base + 0, base + 3, base + 2, base + 1),  # base
        ])

    return MeshData(vertices=verts, faces=faces, name="spike_trap")


# ---------------------------------------------------------------------------
# BLENDER EXPORT
# ---------------------------------------------------------------------------

def meshdata_to_blender(mesh: MeshData, collection_name: str = "ProceduralAssets") -> Optional[str]:
    """Convert MeshData to a Blender mesh object. Returns object name."""
    if not HAS_BLENDER:
        print("[Procedural] Blender not available (bpy not found)")
        return None

    # Ensure collection exists
    if collection_name not in bpy.data.collections:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)
    else:
        coll = bpy.data.collections[collection_name]

    # Create mesh
    bm = bmesh.new()
    vert_map = {}
    for i, co in enumerate(mesh.vertices):
        vert_map[i] = bm.verts.new(co)
    bm.verts.ensure_lookup_table()

    for face_indices in mesh.faces:
        try:
            bm.faces.new([vert_map[i] for i in face_indices])
        except Exception:
            pass  # Duplicate face

    bm.normal_update()

    mesh_data = bpy.data.meshes.new(mesh.name)
    bm.to_mesh(mesh_data)
    bm.free()

    obj = bpy.data.objects.new(mesh.name, mesh_data)
    coll.objects.link(obj)

    # Add simple material
    mat = bpy.data.materials.new(name=f"{mesh.name}_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.6, 0.5, 0.4, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    mesh_data.materials.append(mat)

    return obj.name


def save_blend(filepath: str):
    """Save current Blender session."""
    if HAS_BLENDER:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        print(f"[Procedural] Saved to {filepath}")


def export_obj(filepath: str, objects: Optional[List[str]] = None):
    """Export selected objects as Wavefront OBJ."""
    if not HAS_BLENDER:
        return
    if objects:
        bpy.ops.object.select_all(action='DESELECT')
        for name in objects:
            if name in bpy.data.objects:
                bpy.data.objects[name].select_set(True)
    else:
        bpy.ops.object.select_all(action='SELECT')
    # Blender 4.x/5.x uses wm.obj_export
    if hasattr(bpy.ops.wm, 'obj_export'):
        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
    else:
        # Fallback for older Blender
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=True)
    print(f"[Procedural] Exported OBJ to {filepath}")


def export_fbx(filepath: str, objects: Optional[List[str]] = None):
    """Export selected objects as FBX."""
    if not HAS_BLENDER:
        return
    if objects:
        bpy.ops.object.select_all(action='DESELECT')
        for name in objects:
            if name in bpy.data.objects:
                bpy.data.objects[name].select_set(True)
    else:
        bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
    print(f"[Procedural] Exported FBX to {filepath}")


# ---------------------------------------------------------------------------
# BATCH GENERATION
# ---------------------------------------------------------------------------

def generate_biome(biome_type: str = "forest", count: int = 10, seed: int = 42) -> List[MeshData]:
    """Generate a set of assets for a biome."""
    random.seed(seed)
    assets = []

    if biome_type == "forest":
        assets.append(generate_terrain(size=48, scale=0.08, height=2.5, seed=seed))
        for i in range(count):
            tree = generate_tree(
                trunk_height=random.uniform(1.5, 3.0),
                trunk_radius=random.uniform(0.15, 0.4),
                foliage_radius=random.uniform(0.8, 2.0),
                seed=seed + i
            )
            assets.append(tree)

    elif biome_type == "crystal_cave":
        assets.append(generate_terrain(size=32, scale=0.15, height=1.0, seed=seed))
        for i in range(count):
            crystal = generate_crystal(
                radius=random.uniform(0.3, 1.0),
                height=random.uniform(1.0, 3.0),
                segments=random.randint(5, 8),
                seed=seed + i
            )
            assets.append(crystal)

    elif biome_type == "dungeon":
        assets.append(generate_dungeon_room(
            width=12, depth=12, height=5,
            pillars=random.randint(2, 6),
            seed=seed
        ))
        assets.append(generate_spike_trap(count=3, seed=seed + 1))

    return assets


if __name__ == "__main__":
    # Test without Blender
    print("Testing procedural generators (no Blender)...")
    terrain = generate_terrain(size=16, seed=1)
    print(f"Terrain: {len(terrain.vertices)} verts, {len(terrain.faces)} faces")

    crystal = generate_crystal(seed=2)
    print(f"Crystal: {len(crystal.vertices)} verts, {len(crystal.faces)} faces")

    tree = generate_tree(seed=3)
    print(f"Tree: {len(tree.vertices)} verts, {len(tree.faces)} faces")
