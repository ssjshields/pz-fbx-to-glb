import bpy
import sys
import os
import inspect

# --------------------------------------------------
# Parse CLI args
# --------------------------------------------------
if "--" not in sys.argv:
    print("ERROR: Missing '--' separator")
    sys.exit(1)

argv = sys.argv[sys.argv.index("--") + 1:]

if len(argv) != 2:
    print("ERROR: Expected <input.fbx> <output.glb>")
    print("Got:", argv)
    sys.exit(1)

input_fbx = os.path.abspath(argv[0])
output_glb = os.path.abspath(argv[1])

if not os.path.isfile(input_fbx):
    print("ERROR: Input FBX does not exist")
    print(input_fbx)
    sys.exit(1)

os.makedirs(os.path.dirname(output_glb), exist_ok=True)

print("Input :", input_fbx)
print("Output:", output_glb)

# --------------------------------------------------
# Reset Blender
# --------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

# --------------------------------------------------
# Scene units (meters)
# --------------------------------------------------
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# --------------------------------------------------
# FBX IMPORTER CRASH FIX (LIGHT / CYCLES BUG)
# --------------------------------------------------
scene.render.engine = 'BLENDER_EEVEE'

# --------------------------------------------------
# FBX IMPORTER CRASH FIX (LIGHT / CYCLES BUG)
# --------------------------------------------------
scene.render.engine = 'BLENDER_EEVEE'

# Disable Cycles safely across Blender versions
try:
    bpy.ops.preferences.addon_disable(module="cycles")
except Exception:
    pass


# --------------------------------------------------
# Import FBX (NO animations)
# --------------------------------------------------
bpy.ops.import_scene.fbx(
    filepath=input_fbx,
    use_anim=False,
    use_custom_props=False
)

# --------------------------------------------------
# Convert CM → M (Project Zomboid FIX)
# --------------------------------------------------
for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.scale = (
            obj.scale[0] * 0.01,
            obj.scale[1] * 0.01,
            obj.scale[2] * 0.01,
        )

# --------------------------------------------------
# Apply scale (CRITICAL)
# --------------------------------------------------
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

bpy.ops.object.transform_apply(
    location=False,
    rotation=False,
    scale=True
)

# --------------------------------------------------
# UV KEEP material safety
# --------------------------------------------------
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    if not obj.data.uv_layers:
        continue
    if obj.data.materials:
        continue

    mat = bpy.data.materials.new(name="__UV_KEEP__")
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.interpolation = 'Closest'

    mat.node_tree.links.new(
        tex.outputs["Color"],
        bsdf.inputs["Base Color"]
    )

    obj.data.materials.append(mat)

# --------------------------------------------------
# Safe glTF exporter (version-proof)
# --------------------------------------------------
def gltf_export_safe(filepath, **kwargs):
    op = bpy.ops.export_scene.gltf
    valid = inspect.signature(op).parameters

    filtered = {
        k: v for k, v in kwargs.items()
        if k in valid
    }
    filtered["filepath"] = filepath

    bpy.ops.export_scene.gltf(**filtered)

# --------------------------------------------------
# Export GLB (ASSIMP SAFE)
# --------------------------------------------------
gltf_export_safe(
    filepath=output_glb,
    export_format="GLB",

    export_texcoords=True,
    export_normals=True,
    export_tangents=False,

    export_materials="NONE",
    export_image_format="NONE",

    export_shared_accessors=True,
    export_try_sparse_sk=False,
    export_try_omit_sparse_sk=False,

    export_animations=False,
    export_skins=False,
    export_morph=False,
    export_extras=False,
    export_cameras=False,
    export_lights=False,

    use_selection=True,
    export_yup=True,
    export_apply=False
)