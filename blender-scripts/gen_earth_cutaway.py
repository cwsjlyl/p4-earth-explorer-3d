"""
High-Detail Blender 3D Earth Model ('earth_cutaway.glb') for HK Primary 4 Science (4EA1):
1. Realistic 3D Continents, Oceans, Bathymetry, Himalayas, Polar Ice Caps & South China Coastline
   with 1024x512 PBR BaseColor + Specular Roughness + Normal Maps + Physical 3D Terrain Relief!
2. Semi-Transparent 3D Swirling Atmospheric Cloud Layer ('Layer_Clouds').
3. Textured Convection Magma Mantle ('Layer_Mantle') & Dual-Zone Metallic Core ('Layer_Core').
4. Iconic 3D Hong Kong Landmark Marker ('HK_Marker' + 'anchor_hk') at 22.32°N, 114.17°E
   featuring Bank of China Tower prism, IFC skyscraper, glowing coastal ring & ruby pin!
5. Razor-sharp cutaway cross-sections + 'Basis' (Educational) / 'TrueScale' (Scientific) Shape Keys.
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

from tex_utils import (
    build_pbr_textured_material,
    create_packed_image,
    fbm3d,
    height_to_normal_rgba,
    set_alpha_blend,
    set_emission,
)

# Orient globe so Cutaway Window [270°..360°] slices the mid-Pacific facing the camera (+X, +Z in Three.js),
# while East Asia, China & Hong Kong (22.32°N, 114.17°E -> phi=235°) sit prominently on the sunlit front-left!
LON_OFFSET_DEG = 120.83
HK_LAT_DEG = 22.32
HK_LON_DEG = 114.17


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_solid_mat(name, rgba, roughness=0.45, metallic=0.1, emission_rgba=None, emission_strength=0.0, alpha=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_rgba is not None:
            set_emission(bsdf, emission_rgba, emission_strength)
        if alpha is not None:
            bsdf.inputs["Alpha"].default_value = alpha
            set_alpha_blend(mat)
    return mat


def latlon_to_unit_xyz(lat_deg, lon_deg):
    phi = np.radians((lon_deg + LON_OFFSET_DEG) % 360.0)
    theta = np.radians(90.0 - lat_deg)
    sin_t = np.sin(theta)
    nx = sin_t * np.cos(phi)
    ny = sin_t * np.sin(phi)
    nz = np.cos(theta)
    return nx, ny, nz


def evaluate_world_elevation(lat_deg, lon_deg):
    """
    Vectorized world continent + mountain elevation field in [-1.0 (deep ocean), +1.0 (high peaks)].
    Carefully sculpted so East Asia, South China (Pearl River Delta / Hong Kong), Taiwan, Hainan,
    Japan, Indochina, Australia, India, Eurasia, Africa & Americas are crisp and recognizable.
    """
    nx, ny, nz = latlon_to_unit_xyz(lat_deg, lon_deg)

    # Continental plates: (center_lat, center_lon, sigma_lat, sigma_lon, weight)
    lobes = [
        # China & East Asia (calibrated around South China / Hong Kong 22.3N, 114.2E)
        (31.0, 108.0, 11.5, 13.5, 0.88),   # Central & East China
        (25.2, 113.2, 4.6, 5.8, 0.72),     # Guangdong / South China coast (HK sits right on south coast!)
        (39.5, 116.5, 7.0, 8.5, 0.70),     # North China / Bohai
        (46.0, 126.0, 7.5, 9.0, 0.68),     # Manchuria
        (33.5, 87.0, 7.5, 13.0, 1.18),     # Tibetan Plateau & Himalayas (high snow peaks!)
        (37.5, 127.5, 3.2, 2.2, 0.52),     # Korean Peninsula
        (36.2, 138.5, 4.8, 2.6, 0.56),     # Japan Archipelago
        (23.7, 121.1, 1.7, 1.2, 0.55),     # Taiwan Island
        (19.1, 109.7, 1.4, 1.5, 0.50),     # Hainan Island
        (16.5, 102.5, 6.5, 4.8, 0.68),     # Indochina Peninsula
        (6.0, 101.5, 4.8, 2.0, 0.48),      # Malay Peninsula
        (0.5, 114.0, 4.2, 4.5, 0.56),      # Borneo
        (-2.0, 102.0, 4.5, 2.5, 0.48),     # Sumatra
        (14.5, 121.5, 3.8, 2.0, 0.46),     # Philippines
        # South Asia, Central Eurasia, Siberia, Middle East & Europe
        (21.0, 78.5, 8.5, 6.5, 0.78),      # Indian Subcontinent
        (56.0, 82.0, 13.0, 32.0, 0.82),    # Russia / Siberia
        (60.0, 132.0, 10.0, 22.0, 0.74),   # East Siberia
        (24.5, 45.0, 7.5, 9.0, 0.74),      # Arabian Peninsula
        (36.0, 52.0, 7.5, 12.0, 0.72),     # Iran / Central Asia
        (50.0, 16.0, 9.5, 15.0, 0.74),     # Europe
        (62.0, 15.0, 6.5, 7.5, 0.60),      # Scandinavia
        (54.0, -2.5, 3.2, 2.4, 0.48),      # British Isles
        # Africa
        (18.0, 14.0, 13.0, 18.0, 0.88),    # North Africa / Sahara
        (-4.0, 24.0, 14.0, 11.0, 0.84),    # Central & East Africa
        (-22.0, 24.0, 9.5, 8.0, 0.74),     # Southern Africa
        (-19.0, 46.8, 4.5, 2.2, 0.52),     # Madagascar
        # Australia & New Zealand
        (-24.5, 134.5, 9.0, 13.5, 0.82),   # Australia
        (-41.5, 173.0, 3.5, 2.2, 0.48),    # New Zealand
        # Americas & Antarctica
        (46.0, -102.0, 14.0, 18.0, 0.86),  # North America
        (62.0, -112.0, 10.0, 20.0, 0.74),  # Canada / Alaska
        (21.0, -100.0, 7.0, 5.5, 0.62),    # Mexico / Central America
        (72.0, -42.0, 8.5, 12.0, 0.76),    # Greenland
        (-10.0, -60.0, 13.0, 11.0, 0.86),  # South America (Amazon/Brazil)
        (-34.0, -66.0, 13.0, 5.5, 0.72),   # Patagonia / Andes
        (-84.0, 0.0, 9.0, 180.0, 0.90),    # Antarctica
    ]

    continent = np.zeros_like(lat_deg, dtype=np.float32)
    for clat, clon, slat, slon, w in lobes:
        dlat = (lat_deg - clat) / slat
        # Shortest wrapped longitude delta in [-180, 180]
        dlon = (((lon_deg - clon + 180.0) % 360.0) - 180.0) / slon
        continent += w * np.exp(-0.5 * (dlat * dlat + dlon * dlon))

    # Carve Mediterranean, Red Sea & South China Sea basin so coastlines look crisp
    sea_carves = [
        (15.5, 115.5, 4.8, 5.5, 0.52),   # South China Sea deep basin just SE of HK!
        (36.5, 18.0, 3.5, 12.0, 0.48),   # Mediterranean Sea
        (20.0, 38.5, 5.5, 2.2, 0.42),    # Red Sea
        (25.0, -90.0, 4.8, 6.0, 0.52),   # Gulf of Mexico
    ]
    for clat, clon, slat, slon, w in sea_carves:
        dlat = (lat_deg - clat) / slat
        dlon = (((lon_deg - clon + 180.0) % 360.0) - 180.0) / slon
        continent -= w * np.exp(-0.5 * (dlat * dlat + dlon * dlon))

    # Add organic multi-octave 3D fractal coastline & mountain ridges
    detail = fbm3d(nx * 5.2, ny * 5.2, nz * 5.2, octaves=5, seed=42) - 0.48
    micro_ridge = np.abs(fbm3d(nx * 14.0, ny * 14.0, nz * 14.0, octaves=4, seed=108) - 0.5) * 2.0

    elev = (continent - 0.40) + detail * 0.42 + (1.0 - micro_ridge) * 0.08
    return np.clip(elev, -1.0, 1.2)


def generate_earth_crust_textures(w=1024, h=512):
    """Generates 1K BaseColor, Roughness, and Normal maps aligned to u in [0..1] -> phi in [0..1.5*pi]."""
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    phi_deg = uu * 270.0
    lon_deg = ((phi_deg - LON_OFFSET_DEG + 180.0) % 360.0) - 180.0
    lat_deg = vv * 180.0 - 90.0

    nx, ny, nz = latlon_to_unit_xyz(lat_deg, lon_deg)
    elev = evaluate_world_elevation(lat_deg, lon_deg)
    moisture = fbm3d(nx * 6.5 + 3.1, ny * 6.5 - 1.7, nz * 6.5 + 2.4, octaves=4, seed=303)

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rough = np.ones((h, w, 4), dtype=np.float32)

    # 1. Ocean bathymetry gradient (deep sapphire -> azure -> vibrant coastal turquoise)
    ocean_t = np.clip((elev + 0.65) / 0.65, 0.0, 1.0)
    deep_col = np.array([0.025, 0.11, 0.34], dtype=np.float32)
    mid_col = np.array([0.05, 0.28, 0.62], dtype=np.float32)
    shelf_col = np.array([0.08, 0.62, 0.78], dtype=np.float32)

    ocean_rgb = np.where(
        (ocean_t < 0.72)[..., None],
        deep_col + (ocean_t / 0.72)[..., None] * (mid_col - deep_col),
        mid_col + ((ocean_t - 0.72) / 0.28)[..., None] * (shelf_col - mid_col),
    )

    # 2. Land biomes (coastal sand -> lush emerald forest -> dry ochre desert -> alpine rock -> snow)
    abs_lat = np.abs(lat_deg)
    aridity = np.clip(
        np.exp(-((abs_lat - 24.0) / 11.0) ** 2) * (1.15 - moisture * 1.35)
        - np.exp(-((lon_deg - 112.0) / 18.0) ** 2) * 0.55,  # Keep East/South China lush green!
        0.0,
        1.0,
    )

    lush_green = np.array([0.11, 0.44, 0.16], dtype=np.float32)
    high_forest = np.array([0.18, 0.36, 0.14], dtype=np.float32)
    desert_sand = np.array([0.76, 0.61, 0.36], dtype=np.float32)
    beach_gold = np.array([0.82, 0.74, 0.50], dtype=np.float32)
    alpine_rock = np.array([0.42, 0.37, 0.33], dtype=np.float32)
    snow_white = np.array([0.95, 0.97, 1.00], dtype=np.float32)

    veg_rgb = lush_green * (1.0 - moisture[..., None] * 0.35) + high_forest * (moisture[..., None] * 0.35)
    biome_rgb = veg_rgb * (1.0 - aridity[..., None]) + desert_sand * aridity[..., None]

    # Beach transition right near coastline
    coast_band = np.clip(1.0 - elev / 0.045, 0.0, 1.0)
    biome_rgb = biome_rgb * (1.0 - coast_band[..., None] * 0.65) + beach_gold * (coast_band[..., None] * 0.65)

    # Mountain rock & snow caps (Himalayas + High Latitude Polar Ice)
    mtn_t = np.clip((elev - 0.36) / 0.25, 0.0, 1.0)
    biome_rgb = biome_rgb * (1.0 - mtn_t[..., None]) + alpine_rock * mtn_t[..., None]

    snow_mask = np.clip((elev - 0.56) / 0.16, 0.0, 1.0)
    polar_ice = np.clip((abs_lat - 70.0 + (moisture - 0.5) * 8.0) / 6.0, 0.0, 1.0)
    ice_total = np.maximum(snow_mask, polar_ice)
    land_rgb = biome_rgb * (1.0 - ice_total[..., None]) + snow_white * ice_total[..., None]

    is_land = elev > 0.0
    coast_blend = np.clip(elev / 0.018, 0.0, 1.0)
    final_rgb = np.where(is_land[..., None], ocean_rgb * (1.0 - coast_blend[..., None]) + land_rgb * coast_blend[..., None], ocean_rgb)

    # Polar sea ice pack
    sea_ice = np.clip((abs_lat - 77.0 + (moisture - 0.5) * 6.0) / 4.0, 0.0, 1.0)
    final_rgb = final_rgb * (1.0 - sea_ice[..., None] * 0.85) + snow_white * (sea_ice[..., None] * 0.85)

    rgba[..., :3] = final_rgb

    # Roughness: glossy ocean (0.16), matte land (0.78), icy snow (0.32)
    r_val = np.where(is_land, 0.78 - ice_total * 0.45, 0.16 + sea_ice * 0.25)
    rough[..., 0] = r_val
    rough[..., 1] = r_val
    rough[..., 2] = r_val

    # Bump height only on land & ocean ridges
    bump_h = np.where(is_land, elev * 1.6, elev * 0.12)
    norm_rgba = height_to_normal_rgba(bump_h, strength=4.2)

    img_color = create_packed_image("Tex_Earth_BaseColor", rgba, non_color=False)
    img_rough = create_packed_image("Tex_Earth_Roughness", rough, non_color=True)
    img_norm = create_packed_image("Tex_Earth_Normal", norm_rgba, non_color=True)
    return img_color, img_rough, img_norm


def generate_cloud_texture(w=1024, h=512):
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    phi_deg = uu * 270.0
    lon_deg = ((phi_deg - LON_OFFSET_DEG + 180.0) % 360.0) - 180.0
    lat_deg = vv * 180.0 - 90.0
    nx, ny, nz = latlon_to_unit_xyz(lat_deg, lon_deg)

    # Domain-warped swirling atmospheric cloud bands (ITCZ + mid-latitude cyclones)
    warp = fbm3d(nx * 3.2, ny * 3.2, nz * 3.2, octaves=4, seed=501)
    clouds = fbm3d(
        nx * 6.0 + warp * 1.4,
        ny * 6.0 - warp * 1.2,
        nz * 4.5 + warp * 0.9,
        octaves=5,
        seed=509,
    )
    wisps = fbm3d(nx * 14.0, ny * 14.0, nz * 14.0, octaves=3, seed=521)

    # Keep a subtle clear window right around Hong Kong so the HK skyline marker is super clear,
    # with realistic typhoon/monsoon cloud wisps nearby in the Pacific!
    dhk_lat = (lat_deg - HK_LAT_DEG) / 6.5
    dhk_lon = (((lon_deg - HK_LON_DEG + 180.0) % 360.0) - 180.0) / 7.5
    hk_clear = 1.0 - 0.65 * np.exp(-0.5 * (dhk_lat ** 2 + dhk_lon ** 2))

    density = np.clip((clouds * 0.78 + wisps * 0.22 - 0.50) * 3.1, 0.0, 1.0) * hk_clear
    alpha = np.clip(density ** 1.25 * 0.86, 0.0, 0.88)

    rgba = np.ones((h, w, 4), dtype=np.float32)
    shade = 0.90 + 0.10 * wisps
    rgba[..., 0] = shade
    rgba[..., 1] = shade * 0.99 + 0.01
    rgba[..., 2] = 1.0
    rgba[..., 3] = alpha
    return create_packed_image("Tex_Earth_Clouds", rgba, non_color=False)


def generate_mantle_textures(w=512, h=512):
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    ang = uu * math.pi * 1.5
    nx = np.cos(ang) * np.sin(vv * math.pi)
    ny = np.sin(ang) * np.sin(vv * math.pi)
    nz = np.cos(vv * math.pi)

    warp = fbm3d(nx * 4.0, ny * 4.0, nz * 4.0, octaves=4, seed=701)
    plumes = fbm3d(nx * 7.5 + warp * 1.8, ny * 7.5 - warp * 1.5, nz * 7.5 + warp, octaves=5, seed=719)
    cracks = 1.0 - np.abs(fbm3d(nx * 13.0, ny * 13.0, nz * 13.0, octaves=4, seed=733) - 0.5) * 2.0

    lava_heat = np.clip(plumes * 0.7 + (cracks ** 3) * 0.65 - 0.22, 0.0, 1.0)

    dark_rock = np.array([0.22, 0.05, 0.02], dtype=np.float32)
    crimson_magma = np.array([0.85, 0.18, 0.02], dtype=np.float32)
    bright_lava = np.array([1.00, 0.72, 0.12], dtype=np.float32)

    rgb = np.where(
        (lava_heat < 0.55)[..., None],
        dark_rock + (lava_heat / 0.55)[..., None] * (crimson_magma - dark_rock),
        crimson_magma + ((lava_heat - 0.55) / 0.45)[..., None] * (bright_lava - crimson_magma),
    )

    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    emissive = np.ones((h, w, 4), dtype=np.float32)
    emissive[..., :3] = rgb * (lava_heat[..., None] ** 1.4)

    norm = height_to_normal_rgba(1.0 - lava_heat, strength=3.5)
    return (
        create_packed_image("Tex_Mantle_Color", rgba),
        create_packed_image("Tex_Mantle_Emit", emissive),
        create_packed_image("Tex_Mantle_Normal", norm, non_color=True),
    )


def generate_core_textures(w=512, h=512):
    u = (np.arange(w, dtype=np.float32) + 0.5) / w
    v = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u, v)

    ang = uu * math.pi * 2.0
    nx = np.cos(ang) * np.sin(vv * math.pi)
    ny = np.sin(ang) * np.sin(vv * math.pi)
    nz = np.cos(vv * math.pi)

    swirl = fbm3d(nx * 6.0, ny * 6.0, nz * 6.0, octaves=5, seed=901)
    cryst = np.abs(fbm3d(nx * 16.0, ny * 16.0, nz * 16.0, octaves=3, seed=919) - 0.5) * 2.0

    # uu doubles as radial factor on cutaway walls so inner core shines white-gold!
    hot = np.clip(swirl * 0.75 + (1.0 - cryst) * 0.35, 0.0, 1.0)
    molten_gold = np.array([0.95, 0.56, 0.08], dtype=np.float32)
    white_hot = np.array([1.00, 0.94, 0.62], dtype=np.float32)

    rgb = molten_gold + hot[..., None] * (white_hot - molten_gold)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb

    norm = height_to_normal_rgba(cryst, strength=2.6)
    return (
        create_packed_image("Tex_Core_Color", rgba),
        create_packed_image("Tex_Core_Normal", norm, non_color=True),
    )


def orient_face_outward(face, expected_dir):
    face.normal_update()
    if face.normal.dot(expected_dir) < 0.0:
        face.normal_flip()


def create_cutaway_shell(
    name,
    r_edu_in,
    r_edu_out,
    r_true_in,
    r_true_out,
    seg_u=96,
    seg_v=64,
    mat_outer=None,
    mat_section=None,
    displace_earth_relief=False,
):
    """
    Builds a razor-sharp 270-degree (phi in [0..1.5*pi]) spherical shell leaving [1.5*pi..2*pi] open.
    Unwelded seam edges between outer globe and cross-section walls guarantee crisp 90-degree normals!
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    if mat_outer:
        obj.data.materials.append(mat_outer)
    if mat_section:
        obj.data.materials.append(mat_section)
    sec_mat_idx = 1 if mat_section else 0

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    phi_start = 0.0
    phi_end = math.pi * 1.5

    # Precompute angular grids
    u_vals = np.linspace(0.0, 1.0, seg_u + 1, dtype=np.float32)
    v_vals = np.linspace(0.0, 1.0, seg_v + 1, dtype=np.float32)  # v=0 South Pole, v=1 North Pole
    uu, vv = np.meshgrid(u_vals, v_vals)

    phi_grid = phi_start + uu * (phi_end - phi_start)
    lat_grid = vv * 180.0 - 90.0
    theta_grid = np.radians(90.0 - lat_grid)

    if displace_earth_relief:
        lon_grid = ((np.degrees(phi_grid) - LON_OFFSET_DEG + 180.0) % 360.0) - 180.0
        elev_grid = evaluate_world_elevation(lat_grid, lon_grid)
        # Land rises physically up to +0.068 units; ocean trenches dip slightly
        relief_grid = np.where(elev_grid > 0.0, 0.012 + elev_grid * 0.058, elev_grid * 0.012)
    else:
        relief_grid = np.zeros_like(uu, dtype=np.float32)

    def make_patch_grid(base_radius, use_relief=False):
        grid = []
        for iv in range(seg_v + 1):
            row = []
            for iu in range(seg_u + 1):
                r = base_radius + (float(relief_grid[iv, iu]) if use_relief else 0.0)
                th = float(theta_grid[iv, iu])
                ph = float(phi_grid[iv, iu])
                x = r * math.sin(th) * math.cos(ph)
                y = r * math.sin(th) * math.sin(ph)
                z = r * math.cos(th)
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        return grid

    outer = make_patch_grid(r_edu_out, use_relief=displace_earth_relief)
    for iv in range(seg_v):
        for iu in range(seg_u):
            coords = [
                (iv, iu),
                (iv + 1, iu),
                (iv + 1, iu + 1),
                (iv, iu + 1),
            ]
            verts = [outer[r][c] for r, c in coords]
            # Avoid zero-area degenerate quads at exact poles if needed
            f = bm.faces.new(verts)
            f.material_index = 0
            f.smooth = True
            orient_face_outward(f, f.calc_center_median())
            for loop, (r, c) in zip(f.loops, coords):
                loop[uv_layer].uv = (float(u_vals[c]), float(v_vals[r]))

    if r_edu_in > 0.001:
        inner = make_patch_grid(r_edu_in, use_relief=False)
        for iv in range(seg_v):
            for iu in range(seg_u):
                coords = [
                    (iv, iu),
                    (iv, iu + 1),
                    (iv + 1, iu + 1),
                    (iv + 1, iu),
                ]
                f = bm.faces.new([inner[r][c] for r, c in coords])
                f.material_index = sec_mat_idx
                f.smooth = True
                orient_face_outward(f, -f.calc_center_median())
                for loop, (r, c) in zip(f.loops, coords):
                    loop[uv_layer].uv = (float(u_vals[c]), float(v_vals[r]))

        # Separate crisp vertex strips for the two 90-degree cutaway cross-section walls!
        # Wall A at phi = 0 (+X, y=0): outward normal points into open wedge toward -Y (0, -1, 0)
        w0_in = [bm.verts.new(inner[iv][0].co.copy()) for iv in range(seg_v + 1)]
        w0_out = [bm.verts.new(outer[iv][0].co.copy()) for iv in range(seg_v + 1)]
        for iv in range(seg_v):
            f = bm.faces.new((w0_in[iv], w0_out[iv], w0_out[iv + 1], w0_in[iv + 1]))
            f.material_index = sec_mat_idx
            f.smooth = True
            orient_face_outward(f, Vector((0.0, -1.0, 0.0)))
            uvs = [(0.15, float(v_vals[iv])), (0.85, float(v_vals[iv])), (0.85, float(v_vals[iv + 1])), (0.15, float(v_vals[iv + 1]))]
            for loop, uv in zip(f.loops, uvs):
                loop[uv_layer].uv = uv

        # Wall B at phi = 1.5*pi (x=0, -Y): outward normal points into open wedge toward +X (+1, 0, 0)
        we_in = [bm.verts.new(inner[iv][seg_u].co.copy()) for iv in range(seg_v + 1)]
        we_out = [bm.verts.new(outer[iv][seg_u].co.copy()) for iv in range(seg_v + 1)]
        for iv in range(seg_v):
            f = bm.faces.new((we_in[iv], we_in[iv + 1], we_out[iv + 1], we_out[iv]))
            f.material_index = sec_mat_idx
            f.smooth = True
            orient_face_outward(f, Vector((1.0, 0.0, 0.0)))
            uvs = [(0.15, float(v_vals[iv])), (0.15, float(v_vals[iv + 1])), (0.85, float(v_vals[iv + 1])), (0.85, float(v_vals[iv]))]
            for loop, uv in zip(f.loops, uvs):
                loop[uv_layer].uv = uv
    elif r_edu_in >= 0.0:
        # Solid Core cutaway walls meeting along the Z polar axis (multi-ring radial fan for crisp detail!)
        w0_ax = [bm.verts.new((0.0, 0.0, r_edu_out * math.cos(float(theta_grid[iv, 0])))) for iv in range(seg_v + 1)]
        w0_out = [bm.verts.new(outer[iv][0].co.copy()) for iv in range(seg_v + 1)]
        for iv in range(seg_v):
            f = bm.faces.new((w0_ax[iv], w0_out[iv], w0_out[iv + 1], w0_ax[iv + 1]))
            f.material_index = sec_mat_idx
            f.smooth = True
            orient_face_outward(f, Vector((0.0, -1.0, 0.0)))
            uvs = [(0.95, float(v_vals[iv])), (0.15, float(v_vals[iv])), (0.15, float(v_vals[iv + 1])), (0.95, float(v_vals[iv + 1]))]
            for loop, uv in zip(f.loops, uvs):
                loop[uv_layer].uv = uv

        we_ax = [bm.verts.new((0.0, 0.0, r_edu_out * math.cos(float(theta_grid[iv, seg_u])))) for iv in range(seg_v + 1)]
        we_out = [bm.verts.new(outer[iv][seg_u].co.copy()) for iv in range(seg_v + 1)]
        for iv in range(seg_v):
            f = bm.faces.new((we_ax[iv], we_ax[iv + 1], we_out[iv + 1], we_out[iv]))
            f.material_index = sec_mat_idx
            f.smooth = True
            orient_face_outward(f, Vector((1.0, 0.0, 0.0)))
            uvs = [(0.95, float(v_vals[iv])), (0.95, float(v_vals[iv + 1])), (0.15, float(v_vals[iv + 1])), (0.15, float(v_vals[iv]))]
            for loop, uv in zip(f.loops, uvs):
                loop[uv_layer].uv = uv

    bm.to_mesh(mesh)
    bm.free()

    # Shape Keys: Basis (Educational Scale) -> TrueScale (Scientific Scale)
    if r_true_out > 0.0:
        obj.shape_key_add(name="Basis", from_mix=False)
        sk_true = obj.shape_key_add(name="TrueScale", from_mix=False)
        span_edu = max(r_edu_out - max(r_edu_in, 0.0), 1e-5)
        base_in = max(r_edu_in, 0.0)
        true_in = max(r_true_in, 0.0)
        for i, v in enumerate(mesh.vertices):
            co = v.co
            dist = co.length
            if dist < 1e-5:
                sk_true.data[i].co = co.copy()
            else:
                extra_relief = max(0.0, dist - r_edu_out)
                clamped_d = min(dist, r_edu_out)
                t = max(0.0, min(1.0, (clamped_d - base_in) / span_edu))
                new_r = true_in + t * (r_true_out - true_in) + extra_relief
                sk_true.data[i].co = co.normalized() * new_r

    return obj


def create_cloud_shell(r_cloud, mat_cloud, seg_u=76, seg_v=48):
    mesh = bpy.data.meshes.new("Layer_Clouds_Mesh")
    obj = bpy.data.objects.new("Layer_Clouds", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_cloud)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    phi_start = 0.0
    phi_end = math.pi * 1.5
    u_vals = np.linspace(0.0, 1.0, seg_u + 1, dtype=np.float32)
    v_vals = np.linspace(0.0, 1.0, seg_v + 1, dtype=np.float32)

    grid = []
    for iv in range(seg_v + 1):
        th = math.radians(90.0 - (float(v_vals[iv]) * 180.0 - 90.0))
        row = []
        for iu in range(seg_u + 1):
            ph = phi_start + float(u_vals[iu]) * (phi_end - phi_start)
            x = r_cloud * math.sin(th) * math.cos(ph)
            y = r_cloud * math.sin(th) * math.sin(ph)
            z = r_cloud * math.cos(th)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)

    for iv in range(seg_v):
        for iu in range(seg_u):
            coords = [(iv, iu), (iv + 1, iu), (iv + 1, iu + 1), (iv, iu + 1)]
            f = bm.faces.new([grid[r][c] for r, c in coords])
            f.smooth = True
            orient_face_outward(f, f.calc_center_median())
            for loop, (r, c) in zip(f.loops, coords):
                loop[uv_layer].uv = (float(u_vals[c]), float(v_vals[r]))

    bm.to_mesh(mesh)
    bm.free()
    return obj


def build_hong_kong_landmark(crust_parent, base_radius=2.0):
    """
    Builds an iconic miniature 3D Hong Kong Landmark ('HK_Marker') at 22.32°N, 114.17°E:
    - Glowing Golden-Cyan Victoria Harbour Beacon Ring
    - Stylized Bank of China Tower (中銀大廈 stepped prism + twin spires) & Two IFC Tower
    - Floating Ruby-Red Bauhinia Beacon Pin ('HK_Pin_Gem') + 'anchor_hk' Empty node!
    Parented to Layer_Crust so it moves together when exploding layers!
    """
    hk_elev = float(evaluate_world_elevation(np.array([HK_LAT_DEG]), np.array([HK_LON_DEG]))[0])
    r_surface = base_radius + (0.012 + hk_elev * 0.058 if hk_elev > 0 else 0.015)

    nx, ny, nz = latlon_to_unit_xyz(np.array([HK_LAT_DEG]), np.array([HK_LON_DEG]))
    up_vec = Vector((float(nx[0]), float(ny[0]), float(nz[0]))).normalized()
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(up_vec)

    mat_gold = make_solid_mat(
        "Mat_HK_GoldRing",
        (1.0, 0.84, 0.22, 1.0),
        roughness=0.2,
        metallic=0.85,
        emission_rgba=(1.0, 0.72, 0.12, 1.0),
        emission_strength=0.9,
    )
    mat_skyline = make_solid_mat(
        "Mat_HK_GlassTower",
        (0.55, 0.88, 1.0, 1.0),
        roughness=0.12,
        metallic=0.75,
        emission_rgba=(0.22, 0.75, 1.0, 1.0),
        emission_strength=0.65,
    )
    mat_ruby_pin = make_solid_mat(
        "Mat_HK_RubyBeacon",
        (1.0, 0.14, 0.36, 1.0),
        roughness=0.18,
        metallic=0.25,
        emission_rgba=(1.0, 0.16, 0.42, 1.0),
        emission_strength=1.55,
    )

    # Assemble HK_Marker in a single clean multi-material mesh in local +Z space
    bm = bmesh.new()

    def append_part(temp_obj, mat_idx):
        temp_bm = bmesh.new()
        temp_bm.from_mesh(temp_obj.data)
        for f in temp_bm.faces:
            f.material_index = mat_idx
            f.smooth = True
        # Merge into master bm via temporary mesh
        m_tmp = bpy.data.meshes.new("_tmp_part")
        temp_bm.to_mesh(m_tmp)
        temp_bm.free()
        bm.from_mesh(m_tmp)
        bpy.data.meshes.remove(m_tmp)
        bpy.data.objects.remove(temp_obj, do_unlink=True)

    # 1. Glowing Coastal Base Ring (mat 0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.014, major_segments=28, minor_segments=10, location=(0, 0, 0.008))
    append_part(bpy.context.active_object, 0)

    # 2. Stylized Bank of China Tower (stepped triangular prism + twin antenna needles, mat 1)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.032, radius2=0.018, depth=0.15, location=(-0.018, -0.008, 0.075), rotation=(0, 0, math.pi * 0.25))
    append_part(bpy.context.active_object, 1)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.005, radius2=0.001, depth=0.055, location=(-0.018, -0.008, 0.17))
    append_part(bpy.context.active_object, 0)

    # 3. Stylized Two IFC Skyscraper (mat 1)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.022, depth=0.135, location=(0.022, 0.012, 0.068))
    append_part(bpy.context.active_object, 1)

    # 4. Iconic Floating Ruby Map Pin (inverted cone tip + gem head above skyline, mat 2)
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.048, radius2=0.002, depth=0.095, location=(0, 0, 0.245), rotation=(math.pi, 0, 0))
    append_part(bpy.context.active_object, 2)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.052, location=(0, 0, 0.298))
    append_part(bpy.context.active_object, 2)

    hk_mesh = bpy.data.meshes.new("HK_Marker_Mesh")
    bm.to_mesh(hk_mesh)
    bm.free()

    hk_obj = bpy.data.objects.new("HK_Marker", hk_mesh)
    hk_obj.data.materials.extend([mat_gold, mat_skyline, mat_ruby_pin])
    bpy.context.collection.objects.link(hk_obj)

    hk_obj.parent = crust_parent
    hk_obj.rotation_mode = "QUATERNION"
    hk_obj.rotation_quaternion = rot_quat
    hk_obj.location = up_vec * r_surface

    # Empty anchor right above the ruby pin for crisp 3D HTML badge projection in Three.js!
    anchor_hk = bpy.data.objects.new("anchor_hk", None)
    anchor_hk.empty_display_size = 0.08
    anchor_hk.parent = crust_parent
    anchor_hk.location = up_vec * (r_surface + 0.40)
    bpy.context.collection.objects.link(anchor_hk)


def add_anchor(name, location, parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.15
    empty.location = location
    if parent:
        empty.parent = parent
    bpy.context.collection.objects.link(empty)
    return empty


def build(filepath):
    clear_scene()

    # 1. Build 1K PBR Earth Surface + Continental Bedrock Materials
    img_earth_col, img_earth_rough, img_earth_norm = generate_earth_crust_textures(1024, 512)
    mat_crust_surface = build_pbr_textured_material(
        "Mat_Crust_Surface",
        base_rgba_img=img_earth_col,
        roughness_img=img_earth_rough,
        normal_img=img_earth_norm,
        normal_strength=1.55,
        metallic_val=0.04,
    )
    mat_crust_bedrock = make_solid_mat(
        "Mat_Crust_Bedrock",
        (0.28, 0.24, 0.22, 1.0),
        roughness=0.85,
        metallic=0.08,
    )

    # 2. Build 1K Swirling Cloud Material
    img_clouds = generate_cloud_texture(1024, 512)
    mat_clouds = build_pbr_textured_material(
        "Mat_Atmosphere_Clouds",
        base_rgba_img=img_clouds,
        roughness_val=0.65,
        metallic_val=0.0,
        use_alpha=True,
    )

    # 3. Build 512px Convection Magma Mantle Material
    img_mantle_col, img_mantle_emit, img_mantle_norm = generate_mantle_textures(512, 512)
    mat_mantle = build_pbr_textured_material(
        "Mat_Mantle_Magma",
        base_rgba_img=img_mantle_col,
        normal_img=img_mantle_norm,
        normal_strength=1.4,
        emission_img=img_mantle_emit,
        emission_strength=1.25,
        roughness_val=0.48,
        metallic_val=0.05,
    )

    # 4. Build 512px Molten & Crystalline Iron-Nickel Core Material
    img_core_col, img_core_norm = generate_core_textures(512, 512)
    mat_core = build_pbr_textured_material(
        "Mat_Core_IronNickel",
        base_rgba_img=img_core_col,
        normal_img=img_core_norm,
        normal_strength=1.1,
        emission_img=img_core_col,
        emission_strength=1.15,
        roughness_val=0.20,
        metallic_val=0.88,
    )

    # 5. Construct Concentric 3D Cutaway Shells + Inner Core Crystal Sphere
    core_obj = create_cutaway_shell(
        "Layer_Core",
        0.0,
        0.85,
        0.0,
        1.09,
        seg_u=72,
        seg_v=48,
        mat_outer=mat_core,
        mat_section=mat_core,
        displace_earth_relief=False,
    )

    # Add a gleaming solid Inner Core crystal sphere protruding slightly in the center of the cutaway!
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.42, location=(0.0, 0.0, 0.0))
    inner_core = bpy.context.active_object
    inner_core.name = "Inner_Core_Crystal"
    mat_inner_crystal = make_solid_mat(
        "Mat_Inner_Core_Crystal",
        (1.0, 0.96, 0.76, 1.0),
        roughness=0.14,
        metallic=0.95,
        emission_rgba=(1.0, 0.88, 0.48, 1.0),
        emission_strength=1.6,
    )
    inner_core.data.materials.append(mat_inner_crystal)
    inner_core.parent = core_obj

    mantle_obj = create_cutaway_shell(
        "Layer_Mantle",
        0.86,
        1.72,
        1.10,
        1.955,
        seg_u=84,
        seg_v=56,
        mat_outer=mat_mantle,
        mat_section=mat_mantle,
        displace_earth_relief=False,
    )

    crust_obj = create_cutaway_shell(
        "Layer_Crust",
        1.73,
        2.00,
        1.96,
        2.00,
        seg_u=108,
        seg_v=72,
        mat_outer=mat_crust_surface,
        mat_section=mat_crust_bedrock,
        displace_earth_relief=True,
    )

    create_cloud_shell(2.085, mat_clouds, seg_u=76, seg_v=48)

    # 6. Attach Hong Kong 3D Landmark & Anchors
    build_hong_kong_landmark(crust_obj, base_radius=2.00)

    add_anchor("anchor_core", (0.35, -0.35, 0.15), parent=core_obj)
    add_anchor("anchor_mantle", (0.95, -0.95, 0.35), parent=mantle_obj)
    add_anchor("anchor_crust", (1.42, -1.42, 0.55), parent=crust_obj)

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
        export_morph=True,
    )
