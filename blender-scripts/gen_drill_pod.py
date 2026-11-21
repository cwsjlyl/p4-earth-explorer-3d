"""
High-Detail Industrial Subterranean Exploration Vehicle ('drill_pod.glb'):
- 'Pod_Body': Beveled armored hull with PBR panel-seam & hazard-stripe textures,
  structural rib rings, 4 heavy hydraulic stabilizer fins/skids, twin plasma thrusters & LED searchlights.
- 'Pod_Viewport': Bolted bezel frame, curved sapphire armored dome + interior cockpit console.
- 'Drill_Head': True 3D 3-blade helical spiral tungsten-carbide auger cone + glowing plasma tip!
- 'Drill_Collar': Counter-rotating 12-tooth rock-crushing gear collar!
- 'Heat_Shield': Dual emitter rings + hexagonal honeycomb energy forcefield dome!
"""
import math
import bpy
import bmesh
import numpy as np

from tex_utils import (
    build_pbr_textured_material,
    create_packed_image,
    fbm3d,
    height_to_normal_rgba,
    set_alpha_blend,
    set_emission,
)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def parent_keep_world(child, parent):
    bpy.context.view_layer.update()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def make_mat(name, rgba, metallic=0.5, roughness=0.3, emission=None, strength=0.0, alpha=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None:
            set_emission(bsdf, emission, strength)
        if alpha is not None:
            bsdf.inputs["Alpha"].default_value = alpha
            set_alpha_blend(mat)
    return mat


def generate_armor_textures(w=512, h=512):
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    seam_v = (np.abs(((vv * 6.0) % 1.0) - 0.5) > 0.47).astype(np.float32)
    seam_u = (np.abs(((uu * 8.0) % 1.0) - 0.5) > 0.475).astype(np.float32)
    seams = np.maximum(seam_v, seam_u)

    wear = fbm3d(uu * 18.0, vv * 18.0, np.zeros_like(uu), octaves=3, seed=211)
    yellow_armor = np.array([0.96, 0.68, 0.08], dtype=np.float32)
    dark_steel = np.array([0.16, 0.19, 0.24], dtype=np.float32)

    rgb = yellow_armor * (0.90 + 0.14 * wear[..., None])
    rgb = rgb * (1.0 - seams[..., None] * 0.78) + dark_steel * (seams[..., None] * 0.78)

    in_belt = (vv > 0.16) & (vv < 0.25)
    stripes = (((uu * 24.0 + vv * 18.0) % 1.0) < 0.5).astype(np.float32)
    hazard_rgb = stripes[..., None] * np.array([0.98, 0.78, 0.05], dtype=np.float32) + (1.0 - stripes[..., None]) * np.array([0.08, 0.09, 0.11], dtype=np.float32)
    rgb = np.where(in_belt[..., None], hazard_rgb, rgb)

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    height = 1.0 - seams * 0.8 + wear * 0.15
    norm = height_to_normal_rgba(height, strength=3.2)
    return (
        create_packed_image("Tex_Pod_Armor", rgba),
        create_packed_image("Tex_Pod_Normal", norm, non_color=True),
    )


def generate_hex_shield_texture(w=512, h=256):
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    gx = uu * 28.0
    gy = vv * 14.0
    p1 = np.abs((gx % 1.0) - 0.5)
    p2 = np.abs(((gx * 0.5 + gy * 0.866) % 1.0) - 0.5)
    p3 = np.abs(((gx * 0.5 - gy * 0.866) % 1.0) - 0.5)
    hex_edge = np.maximum(np.maximum(1.0 - p1 * 2.0, 1.0 - p2 * 2.0), 1.0 - p3 * 2.0)
    grid_line = np.clip((hex_edge - 0.78) / 0.22, 0.0, 1.0)

    fade_poles = np.sin(vv * math.pi)
    alpha = np.clip((0.10 + grid_line * 0.62) * fade_poles, 0.0, 0.78)

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., 0] = 0.12 + grid_line * 0.35
    rgba[..., 1] = 0.88 + grid_line * 0.12
    rgba[..., 2] = 0.95
    rgba[..., 3] = alpha
    return create_packed_image("Tex_Hex_Shield", rgba)


def create_spiral_drill_head(mat_tungsten, mat_plasma):
    mesh = bpy.data.meshes.new("Drill_Head_Mesh")
    obj = bpy.data.objects.new("Drill_Head", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_tungsten)
    obj.data.materials.append(mat_plasma)

    bm = bmesh.new()
    rings = 44
    segs = 48
    z_top = -0.34
    z_tip = -1.52

    grid = []
    for ir in range(rings + 1):
        t = ir / rings
        z = z_top + t * (z_tip - z_top)
        base_r = 0.60 * ((1.0 - t) ** 0.82) + 0.015
        row = []
        for iseg in range(segs):
            ang = 2.0 * math.pi * iseg / segs
            spiral_phase = 3.0 * ang + t * (2.5 * 2.0 * math.pi)
            blade = max(0.0, math.sin(spiral_phase)) ** 1.6
            tooth = 0.85 + 0.15 * math.cos(t * 28.0 * math.pi)
            r = base_r + blade * 0.115 * (1.0 - t * 0.78) * tooth
            row.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z)))
        grid.append(row)

    for ir in range(rings):
        is_tip_glow = ir >= rings - 5
        for iseg in range(segs):
            nseg = (iseg + 1) % segs
            f = bm.faces.new((grid[ir][iseg], grid[ir + 1][iseg], grid[ir + 1][nseg], grid[ir][nseg]))
            f.material_index = 1 if is_tip_glow else 0
            f.smooth = True

    top_center = bm.verts.new((0.0, 0.0, z_top))
    tip_center = bm.verts.new((0.0, 0.0, z_tip - 0.04))
    for iseg in range(segs):
        nseg = (iseg + 1) % segs
        f_top = bm.faces.new((top_center, grid[0][iseg], grid[0][nseg]))
        f_top.material_index = 0
        f_tip = bm.faces.new((tip_center, grid[rings][nseg], grid[rings][iseg]))
        f_tip.material_index = 1
        f_tip.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return obj


def create_crusher_collar(mat_gunmetal, mat_gold):
    mesh = bpy.data.meshes.new("Drill_Collar_Mesh")
    obj = bpy.data.objects.new("Drill_Collar", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_gunmetal)
    obj.data.materials.append(mat_gold)

    bm = bmesh.new()
    segs = 48
    z_hi = -0.18
    z_lo = -0.35
    top_ring = []
    bot_ring = []
    in_top = []
    in_bot = []

    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        gear = 0.075 if (i % 4 < 2) else 0.0
        r_out = 0.66 + gear
        r_in = 0.48
        top_ring.append(bm.verts.new((r_out * math.cos(ang), r_out * math.sin(ang), z_hi)))
        bot_ring.append(bm.verts.new((r_out * math.cos(ang), r_out * math.sin(ang), z_lo)))
        in_top.append(bm.verts.new((r_in * math.cos(ang), r_in * math.sin(ang), z_hi)))
        in_bot.append(bm.verts.new((r_in * math.cos(ang), r_in * math.sin(ang), z_lo)))

    for i in range(segs):
        ni = (i + 1) % segs
        is_tooth = i % 4 < 2
        f1 = bm.faces.new((top_ring[i], bot_ring[i], bot_ring[ni], top_ring[ni]))
        f1.material_index = 1 if is_tooth else 0
        bm.faces.new((in_top[i], top_ring[i], top_ring[ni], in_top[ni])).material_index = 0
        bm.faces.new((bot_ring[i], in_bot[i], in_bot[ni], bot_ring[ni])).material_index = 0

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return obj


def build(filepath):
    clear_scene()

    img_armor, img_armor_norm = generate_armor_textures(512, 512)
    mat_armor = build_pbr_textured_material(
        "Mat_Pod_Armor",
        base_rgba_img=img_armor,
        normal_img=img_armor_norm,
        normal_strength=1.45,
        roughness_val=0.34,
        metallic_val=0.58,
    )
    mat_gunmetal = make_mat("Mat_DarkGunmetal", (0.14, 0.17, 0.22, 1.0), metallic=0.86, roughness=0.30)
    mat_tungsten = make_mat("Mat_TungstenDrill", (0.76, 0.80, 0.86, 1.0), metallic=0.94, roughness=0.18)
    mat_plasma = make_mat(
        "Mat_PlasmaTip",
        (1.0, 0.55, 0.12, 1.0),
        metallic=0.2,
        roughness=0.15,
        emission=(1.0, 0.48, 0.08, 1.0),
        strength=2.2,
    )
    mat_glass = make_mat(
        "Mat_CockpitGlass",
        (0.14, 0.78, 1.0, 1.0),
        metallic=0.15,
        roughness=0.06,
        emission=(0.08, 0.52, 0.88, 1.0),
        strength=0.65,
        alpha=0.78,
    )
    mat_thruster_glow = make_mat(
        "Mat_ThrusterPlasma",
        (0.22, 0.94, 1.0, 1.0),
        metallic=0.1,
        roughness=0.1,
        emission=(0.18, 0.90, 1.0, 1.0),
        strength=2.4,
    )
    mat_headlight = make_mat(
        "Mat_HeadlightBeam",
        (1.0, 0.98, 0.86, 1.0),
        metallic=0.1,
        roughness=0.1,
        emission=(1.0, 0.96, 0.78, 1.0),
        strength=2.8,
    )

    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=24, radius=0.70, location=(0, 0, 0.36))
    hull = bpy.context.active_object
    hull.name = "Pod_Body"
    hull.scale = (1.0, 1.0, 1.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    hull.data.materials.append(mat_armor)
    for p in hull.data.polygons:
        p.use_smooth = True

    for idx, z_pos in enumerate((0.02, 0.38, 0.74)):
        r_maj = 0.71 if idx == 1 else 0.62
        bpy.ops.mesh.primitive_torus_add(major_radius=r_maj, minor_radius=0.042, major_segments=36, minor_segments=12, location=(0, 0, z_pos))
        rib = bpy.context.active_object
        rib.name = f"Hull_Rib_{idx}"
        rib.data.materials.append(mat_gunmetal)
        for p in rib.data.polygons:
            p.use_smooth = True
        parent_keep_world(rib, hull)

    for i in range(4):
        ang = math.pi * 0.25 + i * (math.pi * 0.5)
        fx = math.cos(ang) * 0.72
        fy = math.sin(ang) * 0.72
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, 0.26), rotation=(0, 0, ang))
        fin = bpy.context.active_object
        fin.name = f"Stabilizer_Fin_{i}"
        fin.scale = (0.22, 0.08, 0.62)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bev = fin.modifiers.new(name="Bevel", type="BEVEL")
        bev.width = 0.022
        bev.segments = 2
        fin.data.materials.append(mat_gunmetal)
        parent_keep_world(fin, hull)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.20, radius2=0.13, depth=0.28, location=(side * 0.28, 0.0, 1.25))
        nozzle = bpy.context.active_object
        nozzle.data.materials.append(mat_gunmetal)
        parent_keep_world(nozzle, hull)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.12, location=(side * 0.28, 0.0, 1.36))
        flame = bpy.context.active_object
        flame.data.materials.append(mat_thruster_glow)
        parent_keep_world(flame, hull)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=18,
            radius=0.11,
            depth=0.22,
            location=(side * 0.54, -0.38, 0.68),
            rotation=(math.pi * 0.42, 0, 0),
        )
        pod_light = bpy.context.active_object
        pod_light.data.materials.append(mat_gunmetal)
        parent_keep_world(pod_light, hull)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.088, location=(side * 0.54, -0.48, 0.65))
        lens = bpy.context.active_object
        lens.data.materials.append(mat_headlight)
        parent_keep_world(lens, hull)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.38,
        minor_radius=0.05,
        major_segments=28,
        minor_segments=12,
        location=(0, -0.56, 0.44),
        rotation=(math.pi * 0.46, 0, 0),
    )
    bezel = bpy.context.active_object
    bezel.name = "Viewport_Bezel"
    bezel.data.materials.append(mat_gunmetal)
    parent_keep_world(bezel, hull)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.14, location=(0, -0.42, 0.40))
    holo = bpy.context.active_object
    holo.name = "Cockpit_HoloGlobe"
    holo.data.materials.append(mat_thruster_glow)
    parent_keep_world(holo, hull)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=26, ring_count=18, radius=0.37, location=(0, -0.52, 0.44))
    glass = bpy.context.active_object
    glass.name = "Pod_Viewport"
    glass.data.materials.append(mat_glass)
    for p in glass.data.polygons:
        p.use_smooth = True
    parent_keep_world(glass, hull)

    create_spiral_drill_head(mat_tungsten, mat_plasma)
    create_crusher_collar(mat_gunmetal, mat_armor)

    img_hex = generate_hex_shield_texture(512, 256)
    mat_hex_shield = build_pbr_textured_material(
        "Mat_HexForcefield",
        base_rgba_img=img_hex,
        emission_img=img_hex,
        emission_strength=1.35,
        roughness_val=0.15,
        metallic_val=0.1,
        use_alpha=True,
    )

    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=24, radius=1.08, location=(0, 0, 0.10))
    shield = bpy.context.active_object
    shield.name = "Heat_Shield"
    shield.scale = (1.0, 1.0, 1.38)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shield.data.materials.append(mat_hex_shield)
    for p in shield.data.polygons:
        p.use_smooth = True

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
    )
