import bpy
import sys
import os
import inspect

# ==================================================
# HARD LOCK: Blender 4.2 LTS ONLY
# ==================================================
ver = bpy.app.version
if not (ver[0] == 4 and ver[1] == 2):
    print(f"ERROR: Unsupported Blender version {ver}")
    print("This tool is LOCKED to Blender 4.2 LTS for Project Zomboid.")
    sys.exit(1)

# ==================================================
# Parse CLI args
# ==================================================
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
    sys.exit(1)

os.makedirs(os.path.dirname(output_glb), exist_ok=True)

print("Input :", input_fbx)
print("Output:", output_glb)

# ==================================================
# Reset Blender cleanly
# ==================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Force Eevee (Cycles not needed)
# scene.render.engine = "BLENDER_EEVEE"

# ==================================================
# Scene units (meters, PZ-safe)
# ==================================================
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

# ==================================================
# FBX IMPORT (LOCKED SAFE FLAGS)
# ==================================================
bpy.ops.import_scene.fbx(
    filepath=input_fbx,
    use_anim=False,
    use_custom_normals=True,
    ignore_leaf_bones=True,
    # use_lights=False,     # 🔒 critical
    # use_cameras=False,   # 🔒 critical
)

# ==================================================
# Remove any leftover lights/cameras (paranoia)
# ==================================================
for obj in list(bpy.data.objects):
    if obj.type in {"LIGHT", "CAMERA"}:
        bpy.data.objects.remove(obj, do_unlink=True)

mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
if not mesh_objs:
    print("ERROR: No mesh objects imported")
    sys.exit(1)

# ==================================================
# Scale fix (cm → m safety net)
# ==================================================
for obj in mesh_objs:
    if max(obj.dimensions) > 10.0:
        obj.scale = (0.01, 0.01, 0.01)

# ==================================================
# Apply transforms
# ==================================================
bpy.ops.object.select_all(action="DESELECT")
for obj in mesh_objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# ==================================================
# Force visible PZ-safe material
# ==================================================
for obj in mesh_objs:
    mat = bpy.data.materials.new(name="__PZ_MAT__")
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    output = nodes.new("ShaderNodeOutputMaterial")

    bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bsdf.inputs["Alpha"].default_value = 1.0

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)

# ==================================================
# GLTF EXPORT (PZ LOCKED)
# ==================================================
bpy.ops.object.select_all(action="DESELECT")
for obj in mesh_objs:
    obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format="GLB",
    export_materials="EXPORT",
    export_image_format="NONE",
    export_texcoords=True,
    export_normals=True,
    export_animations=False,
    export_skins=False,
    export_morph=False,
    export_lights=False,
    export_cameras=False,
    use_selection=True,
    export_yup=True,
    export_apply=False,
)

print("SUCCESS: Project Zomboid GLB exported cleanly")
