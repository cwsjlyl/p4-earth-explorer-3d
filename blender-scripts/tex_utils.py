"""
Procedural PBR Texture & Normal Map utilities using NumPy for Headless Blender 5.x.
Generates crisp 1K/512px BaseColor, Roughness, Emission, Alpha & Tangent Normal maps
and packs them directly into .glb exports.
"""
import os
import tempfile
import bpy
import numpy as np


def _quintic(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _hash3(ix, iy, iz, seed):
    # Fast deterministic 3D integer hash in [0, 1] using int64 to avoid overflow warnings
    ix = ix.astype(np.int64)
    iy = iy.astype(np.int64)
    iz = iz.astype(np.int64)
    n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ np.int64(seed * 26544357)
    n = (n ^ (n >> 13)) * 1274126177
    n = (n ^ (n >> 16)) & 0x7FFFFFFF
    return n.astype(np.float32) / float(0x7FFFFFFF)


def noise3d(x, y, z, seed=0):
    ix = np.floor(x).astype(np.int64)
    iy = np.floor(y).astype(np.int64)
    iz = np.floor(z).astype(np.int64)

    fx = _quintic((x - ix).astype(np.float32))
    fy = _quintic((y - iy).astype(np.float32))
    fz = _quintic((z - iz).astype(np.float32))

    c000 = _hash3(ix, iy, iz, seed)
    c100 = _hash3(ix + 1, iy, iz, seed)
    c010 = _hash3(ix, iy + 1, iz, seed)
    c110 = _hash3(ix + 1, iy + 1, iz, seed)
    c001 = _hash3(ix, iy, iz + 1, seed)
    c101 = _hash3(ix + 1, iy, iz + 1, seed)
    c011 = _hash3(ix, iy + 1, iz + 1, seed)
    c111 = _hash3(ix + 1, iy + 1, iz + 1, seed)

    c00 = c000 + fx * (c100 - c000)
    c10 = c010 + fx * (c110 - c010)
    c01 = c001 + fx * (c101 - c001)
    c11 = c011 + fx * (c111 - c011)

    c0 = c00 + fy * (c10 - c00)
    c1 = c01 + fy * (c11 - c01)
    return c0 + fz * (c1 - c0)


def fbm3d(x, y, z, octaves=5, lacunarity=2.05, gain=0.5, seed=1):
    total = np.zeros_like(x, dtype=np.float32)
    amp = 0.5
    freq = 1.0
    norm = 0.0
    for i in range(octaves):
        total += amp * noise3d(x * freq, y * freq, z * freq, seed=seed + i * 17)
        norm += amp
        freq *= lacunarity
        amp *= gain
    return total / max(norm, 1e-6)


def height_to_normal_rgba(height_2d, strength=3.0):
    gy, gx = np.gradient(height_2d.astype(np.float32))
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(nx, dtype=np.float32)
    inv_len = 1.0 / np.maximum(np.sqrt(nx * nx + ny * ny + nz * nz), 1e-6)
    nx *= inv_len
    ny *= inv_len
    nz *= inv_len

    rgba = np.ones((height_2d.shape[0], height_2d.shape[1], 4), dtype=np.float32)
    rgba[..., 0] = nx * 0.5 + 0.5
    rgba[..., 1] = ny * 0.5 + 0.5
    rgba[..., 2] = nz * 0.5 + 0.5
    return rgba


def create_packed_image(name, rgba, non_color=False):
    h, w, _ = rgba.shape
    clipped = np.clip(rgba, 0.0, 1.0).astype(np.float32)
    img = bpy.data.images.new(name=name, width=w, height=h, alpha=True, is_data=non_color)
    if non_color:
        try:
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
    img.pixels.foreach_set(clipped.ravel())
    tmp_path = os.path.join(tempfile.gettempdir(), f"{name}.png")
    img.filepath_raw = tmp_path
    img.file_format = "PNG"
    img.save()
    img.pack()
    if non_color:
        try:
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
    return img


def set_alpha_blend(mat):
    if hasattr(mat, "surface_render_method"):
        try:
            mat.surface_render_method = "BLENDED"
        except Exception:
            pass
    if hasattr(mat, "blend_method"):
        try:
            mat.blend_method = "BLEND"
        except Exception:
            pass


def set_emission(bsdf, color_rgba, strength):
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = color_rgba
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = color_rgba
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = strength


def build_pbr_textured_material(
    name,
    base_rgba_img=None,
    normal_img=None,
    normal_strength=1.2,
    roughness_img=None,
    emission_img=None,
    emission_strength=0.0,
    roughness_val=0.5,
    metallic_val=0.0,
    use_alpha=False,
):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    bsdf.inputs["Roughness"].default_value = roughness_val
    bsdf.inputs["Metallic"].default_value = metallic_val

    if base_rgba_img is not None:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.image = base_rgba_img
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        if use_alpha:
            links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
            set_alpha_blend(mat)

    if roughness_img is not None:
        r_node = nodes.new("ShaderNodeTexImage")
        r_node.image = roughness_img
        links.new(r_node.outputs["Color"], bsdf.inputs["Roughness"])

    if emission_img is not None and emission_strength > 0.0:
        e_node = nodes.new("ShaderNodeTexImage")
        e_node.image = emission_img
        em_socket = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        links.new(e_node.outputs["Color"], bsdf.inputs[em_socket])
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    if normal_img is not None:
        n_tex = nodes.new("ShaderNodeTexImage")
        n_tex.image = normal_img
        n_map = nodes.new("ShaderNodeNormalMap")
        n_map.inputs["Strength"].default_value = normal_strength
        links.new(n_tex.outputs["Color"], n_map.inputs["Color"])
        links.new(n_map.outputs["Normal"], bsdf.inputs["Normal"])

    return mat
