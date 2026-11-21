"""
Museum-Grade Hong Kong Geological Rock Specimens ('rock_samples.glb') for Primary 4 (4EA2):
1. 'Rock_Granite' (花崗岩 - Igneous): Angular fractured crystalline outcrop with authentic
   pink potassium feldspar, grey-white quartz & black biotite mica mineral speckles + crystal normal facets!
2. 'Rock_Sandstone' (砂岩 - Sedimentary): Tabular stepped cliff specimen with authentic
   Hong Kong Port Island (赤洲) terracotta-red & golden-ochre horizontal bedding strata + sandy grain bump!
3. 'Rock_Marble' (大理岩 - Metamorphic): Semi-polished sculpted stone with authentic
   alabaster-white & turbulent grey-gold metamorphic flow veins + glossy polish!
Each mounted on an obsidian-slate museum display pedestal with a brass trim ring.
"""
import math
import bpy
import numpy as np

from tex_utils import (
    build_pbr_textured_material,
    create_packed_image,
    fbm3d,
    height_to_normal_rgba,
     noise3d,
)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_solid_mat(name, rgba, metallic=0.2, roughness=0.4):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def generate_granite_textures(w=512, h=512):
    """Authentic Hong Kong Pink-Grey Biotite Granite with distinct mineral crystal grains."""
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    # High-frequency cellular/crystalline mineral grain noise
    g1 = noise3d(uu * 46.0, vv * 46.0, np.zeros_like(uu) + 1.2, seed=101)
    g2 = noise3d(uu * 92.0 + 4.5, vv * 92.0 - 2.3, np.zeros_like(uu) + 3.7, seed=107)
    macro = fbm3d(uu * 8.0, vv * 8.0, np.zeros_like(uu), octaves=3, seed=113)

    grain = g1 * 0.65 + g2 * 0.35

    quartz_rgb = np.array([0.84, 0.85, 0.87], dtype=np.float32)       # Translucent grey-white quartz
    feldspar_rgb = np.array([0.91, 0.76, 0.72], dtype=np.float32)     # Hong Kong pinkish-cream feldspar
    biotite_rgb = np.array([0.09, 0.10, 0.12], dtype=np.float32)      # Crisp black biotite mica flakes

    # Partition grains sharply into biotite (<0.27), feldspar (0.27..0.60), quartz (>0.60)
    rgb = np.where(
        (grain < 0.27)[..., None],
        biotite_rgb,
        np.where((grain < 0.60)[..., None], feldspar_rgb, quartz_rgb),
    )
    rgb *= 0.88 + 0.22 * macro[..., None]

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    norm = height_to_normal_rgba(grain * 0.7 + macro * 0.3, strength=3.8)
    return (
        create_packed_image("Tex_Granite_Color", rgba),
        create_packed_image("Tex_Granite_Normal", norm, non_color=True),
    )


def generate_sandstone_textures(w=512, h=512):
    """Authentic Hong Kong Port Island (赤洲) Reddish-Ochre Layered Sedimentary Sandstone."""
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    # Gently undulating horizontal sedimentary bedding planes along vv
    wave = fbm3d(uu * 4.5, vv * 4.5, np.zeros_like(uu), octaves=3, seed=201) * 0.085
    strata_coord = vv * 14.0 + wave * 10.0
    strata = np.sin(strata_coord * math.pi * 2.0) * 0.5 + 0.5
    fine_beds = fbm3d(uu * 2.0, strata_coord * 3.5, np.zeros_like(uu), octaves=4, seed=211)
    sand_grit = noise3d(uu * 130.0, vv * 130.0, np.zeros_like(uu), seed=223)

    terracotta = np.array([0.74, 0.31, 0.18], dtype=np.float32)
    ochre_gold = np.array([0.87, 0.64, 0.34], dtype=np.float32)
    buff_cream = np.array([0.92, 0.80, 0.58], dtype=np.float32)

    mix1 = terracotta + strata[..., None] * (ochre_gold - terracotta)
    rgb = mix1 * (1.0 - fine_beds[..., None] * 0.48) + buff_cream * (fine_beds[..., None] * 0.48)
    rgb *= 0.90 + 0.18 * sand_grit[..., None]

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    height = strata * 0.55 + fine_beds * 0.30 + sand_grit * 0.25
    norm = height_to_normal_rgba(height, strength=4.2)
    return (
        create_packed_image("Tex_Sandstone_Color", rgba),
        create_packed_image("Tex_Sandstone_Normal", norm, non_color=True),
    )


def generate_marble_textures(w=512, h=512):
    """Polished Pearl-White Metamorphic Marble with turbulent grey-slate & champagne veins."""
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    warp1 = fbm3d(uu * 4.2, vv * 4.2, np.zeros_like(uu), octaves=5, seed=301)
    warp2 = fbm3d(uu * 8.5 + warp1 * 2.4, vv * 8.5 - warp1 * 2.1, np.zeros_like(uu), octaves=5, seed=313)

    vein_primary = np.exp(-((np.sin((uu * 3.5 + vv * 2.8 + warp2 * 2.6) * math.pi)) ** 2) / 0.018)
    vein_gold = np.exp(-((np.sin((uu * 5.2 - vv * 4.1 + warp1 * 3.1) * math.pi)) ** 2) / 0.008)

    pearl_white = np.array([0.95, 0.96, 0.97], dtype=np.float32)
    slate_vein = np.array([0.34, 0.40, 0.48], dtype=np.float32)
    gold_vein = np.array([0.78, 0.65, 0.38], dtype=np.float32)

    rgb = pearl_white * (0.95 + 0.05 * warp1[..., None])
    rgb = rgb * (1.0 - vein_primary[..., None] * 0.72) + slate_vein * (vein_primary[..., None] * 0.72)
    rgb = rgb * (1.0 - vein_gold[..., None] * 0.45) + gold_vein * (vein_gold[..., None] * 0.45)

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    norm = height_to_normal_rgba(1.0 - vein_primary * 0.4, strength=1.2)
    return (
        create_packed_image("Tex_Marble_Color", rgba),
        create_packed_image("Tex_Marble_Normal", norm, non_color=True),
    )


def add_museum_pedestal(parent_rock, mat_plinth, mat_brass):
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.78, depth=0.16, location=(0.0, 0.0, -0.62))
    base = bpy.context.active_object
    bev = base.modifiers.new(name="Bevel", type="BEVEL")
    bev.width = 0.025
    bev.segments = 2
    base.data.materials.append(mat_plinth)
    for p in base.data.polygons:
        p.use_smooth = True
    base.parent = parent_rock

    bpy.ops.mesh.primitive_torus_add(major_radius=0.76, minor_radius=0.018, major_segments=36, minor_segments=10, location=(0.0, 0.0, -0.54))
    ring = bpy.context.active_object
    ring.data.materials.append(mat_brass)
    for p in ring.data.polygons:
        p.use_smooth = True
    ring.parent = parent_rock


def sculpt_specimen(name, location, mode, mat_rock, mat_plinth, mat_brass):
    # UV sphere gives clean equirectangular UVs so strata/grain textures wrap seamlessly!
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48, radius=0.68, location=location)
    obj = bpy.context.active_object
    obj.name = name

    coords = np.array([ [v.co.x, v.co.y, v.co.z] for v in obj.data.vertices ], dtype=np.float32)
    nx = coords[:, 0] / 0.68
    ny = coords[:, 1] / 0.68
    nz = coords[:, 2] / 0.68

    if mode == "granite":
        # Angular fractured crystalline granite boulder (planar fracture cuts + coarse ridges)
        planes = [
            (0.75, -0.45, 0.48, 0.52),
            (-0.68, -0.52, 0.51, 0.54),
            (0.15, 0.82, 0.55, 0.56),
            (-0.55, 0.45, -0.68, 0.55),
        ]
        r_scale = 0.88 + 0.24 * fbm3d(nx * 3.2, ny * 3.2, nz * 3.2, octaves=4, seed=601)
        coords *= r_scale[:, None]
        for px, py, pz, limit in planes:
            dot = coords[:, 0] * px + coords[:, 1] * py + coords[:, 2] * pz
            excess = np.maximum(0.0, dot - limit)
            coords[:, 0] -= excess * px * 0.82
            coords[:, 1] -= excess * py * 0.82
            coords[:, 2] -= excess * pz * 0.82
        coords[:, 2] *= 0.86

    elif mode == "sandstone":
        # Tabular stepped sedimentary cliff block with physical horizontal bedding ledges!
        terrace = np.sin(nz * 16.0) * 0.045 + fbm3d(nx * 3.5, ny * 3.5, nz * 6.0, octaves=4, seed=617) * 0.18
        coords[:, 0] *= (1.16 + terrace)
        coords[:, 1] *= (0.96 + terrace)
        coords[:, 2] = np.clip(coords[:, 2] * 0.76, -0.48, 0.48)

    elif mode == "marble":
        # Sculpted metamorphic stone with a sleek polished inspection face on the front (-Y -> +Z in Three.js)
        flow = 0.92 + 0.16 * fbm3d(nx * 2.6, ny * 2.6, nz * 2.6, octaves=3, seed=631)
        coords *= flow[:, None]
        # Carve a smooth, gleaming diagonal polished face facing the viewer!
        cut_dir = np.array([0.28, -0.82, 0.48], dtype=np.float32)
        cut_dir /= np.linalg.norm(cut_dir)
        dot = coords @ cut_dir
        excess = np.maximum(0.0, dot - 0.38)
        coords -= excess[:, None] * cut_dir[None, :] * 0.94

    # Rest bottom cleanly above pedestal at z = -0.52
    min_z = float(np.min(coords[:, 2]))
    coords[:, 2] += (-0.52 - min_z)

    for i, v in enumerate(obj.data.vertices):
        v.co.x = float(coords[i, 0])
        v.co.y = float(coords[i, 1])
        v.co.z = float(coords[i, 2])

    obj.data.update()
    for p in obj.data.polygons:
        p.use_smooth = mode != "granite"

    obj.data.materials.append(mat_rock)
    add_museum_pedestal(obj, mat_plinth, mat_brass)
    return obj


def build(filepath):
    clear_scene()

    mat_plinth = make_solid_mat("Mat_MuseumPlinth", (0.09, 0.11, 0.16, 1.0), metallic=0.35, roughness=0.28)
    mat_brass = make_solid_mat("Mat_MuseumBrass", (0.92, 0.74, 0.28, 1.0), metallic=0.88, roughness=0.22)

    img_gran_col, img_gran_norm = generate_granite_textures(512, 512)
    mat_granite = build_pbr_textured_material(
        "Mat_HK_Granite",
        base_rgba_img=img_gran_col,
        normal_img=img_gran_norm,
        normal_strength=1.65,
        roughness_val=0.46,
        metallic_val=0.08,
    )

    img_sand_col, img_sand_norm = generate_sandstone_textures(512, 512)
    mat_sandstone = build_pbr_textured_material(
        "Mat_HK_Sandstone",
        base_rgba_img=img_sand_col,
        normal_img=img_sand_norm,
        normal_strength=1.85,
        roughness_val=0.88,
        metallic_val=0.02,
    )

    img_marb_col, img_marb_norm = generate_marble_textures(512, 512)
    mat_marble = build_pbr_textured_material(
        "Mat_HK_Marble",
        base_rgba_img=img_marb_col,
        normal_img=img_marb_norm,
        normal_strength=0.65,
        roughness_val=0.14,
        metallic_val=0.06,
    )

    sculpt_specimen("Rock_Granite", (-2.1, 0.0, 0.0), "granite", mat_granite, mat_plinth, mat_brass)
    sculpt_specimen("Rock_Sandstone", (0.0, 0.0, 0.0), "sandstone", mat_sandstone, mat_plinth, mat_brass)
    sculpt_specimen("Rock_Marble", (2.1, 0.0, 0.0), "marble", mat_marble, mat_plinth, mat_brass)

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
    )
