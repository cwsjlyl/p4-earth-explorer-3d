"""
Generates the 3 Primary 4 curriculum rock specimens (4EA2 extension):
- Rock_Granite (花崗岩 - Igneous)
- Rock_Sandstone (砂岩 - Sedimentary)
- Rock_Marble (大理岩 - Metamorphic)
"""
import random
import bpy


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_mat(name, rgba, roughness=0.75, metallic=0.05):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def sculpt_rock(name, location, scale_xyz, seed, flat_shade, mat):
    rng = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.65, location=location)
    obj = bpy.context.active_object
    obj.name = name
    for v in obj.data.vertices:
        jitter = 0.84 + rng.random() * 0.32
        v.co.x *= scale_xyz[0] * jitter
        v.co.y *= scale_xyz[1] * jitter
        v.co.z *= scale_xyz[2] * jitter
    for p in obj.data.polygons:
        p.use_smooth = not flat_shade
    obj.data.materials.append(mat)
    return obj


def build(filepath):
    clear_scene()

    mat_granite = make_mat("Mat_Granite", (0.76, 0.73, 0.72, 1.0), roughness=0.65, metallic=0.12)
    mat_sandstone = make_mat("Mat_Sandstone", (0.85, 0.66, 0.38, 1.0), roughness=0.92, metallic=0.0)
    mat_marble = make_mat("Mat_Marble", (0.93, 0.94, 0.96, 1.0), roughness=0.25, metallic=0.08)

    sculpt_rock("Rock_Granite", (-1.8, 0.0, 0.0), (1.05, 0.95, 0.90), seed=401, flat_shade=True, mat=mat_granite)
    sculpt_rock("Rock_Sandstone", (0.0, 0.0, 0.0), (1.20, 1.00, 0.68), seed=402, flat_shade=True, mat=mat_sandstone)
    sculpt_rock("Rock_Marble", (1.8, 0.0, 0.0), (0.98, 0.98, 0.92), seed=403, flat_shade=False, mat=mat_marble)

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
    )
