"""
Generates a cute Q-version subterranean exploration pod ('drill_pod.glb')
with separate 'Drill_Head' and 'Heat_Shield' meshes for Three.js animation.
"""
import math
import bpy


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_mat(name, rgba, metallic=0.3, roughness=0.35, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def build(filepath):
    clear_scene()

    mat_hull = make_mat("Mat_PodHull", (0.96, 0.72, 0.12, 1.0), metallic=0.45, roughness=0.28)
    mat_glass = make_mat(
        "Mat_PodViewport",
        (0.20, 0.85, 1.0, 1.0),
        metallic=0.1,
        roughness=0.1,
        emission=(0.15, 0.75, 1.0, 1.0),
        strength=0.6,
    )
    mat_drill = make_mat("Mat_DrillTitanium", (0.72, 0.76, 0.82, 1.0), metallic=0.9, roughness=0.22)
    mat_shield = make_mat(
        "Mat_ThermalShield",
        (0.18, 0.92, 0.78, 1.0),
        metallic=0.2,
        roughness=0.2,
        emission=(0.1, 0.85, 0.72, 1.0),
        strength=0.5,
    )

    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=16, radius=0.65, location=(0, 0, 0.25))
    hull = bpy.context.active_object
    hull.name = "Pod_Body"
    hull.scale = (1.0, 1.0, 1.18)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    hull.data.materials.append(mat_hull)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.34, location=(0, -0.46, 0.35))
    cockpit = bpy.context.active_object
    cockpit.name = "Pod_Viewport"
    cockpit.data.materials.append(mat_glass)

    bpy.ops.mesh.primitive_cone_add(
        vertices=18,
        radius1=0.52,
        radius2=0.02,
        depth=0.95,
        location=(0, 0, -0.82),
        rotation=(math.pi, 0, 0),
    )
    drill = bpy.context.active_object
    drill.name = "Drill_Head"
    drill.data.materials.append(mat_drill)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.76,
        minor_radius=0.07,
        major_segments=28,
        minor_segments=12,
        location=(0, 0, -0.15),
    )
    shield = bpy.context.active_object
    shield.name = "Heat_Shield"
    shield.data.materials.append(mat_shield)

    for obj in bpy.context.collection.objects:
        if obj.type == "MESH":
            for p in obj.data.polygons:
                p.use_smooth = True

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
    )
