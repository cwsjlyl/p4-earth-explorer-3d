"""
Generates a 3/4 cutaway Earth model (Crust, Mantle, Core) with:
- Watertight cross-section faces so students can inspect internal thickness
- Shape Keys ('Basis' = Educational Scale for easy iPad touch, 'TrueScale' = Scientific Scale)
- Empty anchor nodes for 3D labels
Compatible with Blender 3.6 and 4.x+.
"""
import math
import bpy
import bmesh


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, base_rgba, roughness=0.6, metallic=0.0, emission_rgba=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_rgba is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_rgba
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_rgba
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def create_cutaway_shell(name, r_edu_in, r_edu_out, r_true_in, r_true_out, seg_u=42, seg_v=24, mat=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    phi_start = math.pi * 0.5
    phi_end = math.pi * 2.0

    def ring_grid(radius):
        grid = []
        for iv in range(seg_v + 1):
            theta = math.pi * iv / seg_v
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            row = []
            for iu in range(seg_u + 1):
                phi = phi_start + (phi_end - phi_start) * (iu / seg_u)
                x = radius * sin_t * math.cos(phi)
                y = radius * sin_t * math.sin(phi)
                z = radius * cos_t
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        return grid

    outer = ring_grid(r_edu_out)
    inner = ring_grid(r_edu_in) if r_edu_in > 0.001 else None

    for iv in range(seg_v):
        for iu in range(seg_u):
            v1 = outer[iv][iu]
            v2 = outer[iv + 1][iu]
            v3 = outer[iv + 1][iu + 1]
            v4 = outer[iv][iu + 1]
            bm.faces.new((v1, v2, v3, v4))

    if inner is not None:
        for iv in range(seg_v):
            for iu in range(seg_u):
                v1 = inner[iv][iu]
                v2 = inner[iv][iu + 1]
                v3 = inner[iv + 1][iu + 1]
                v4 = inner[iv + 1][iu]
                bm.faces.new((v1, v2, v3, v4))

        for iv in range(seg_v):
            bm.faces.new((inner[iv][0], inner[iv + 1][0], outer[iv + 1][0], outer[iv][0]))
            bm.faces.new((outer[iv][seg_u], outer[iv + 1][seg_u], inner[iv + 1][seg_u], inner[iv][seg_u]))
    else:
        center_verts = [
            bm.verts.new((0.0, 0.0, r_edu_out * math.cos(math.pi * iv / seg_v)))
            for iv in range(seg_v + 1)
        ]
        for iv in range(seg_v):
            bm.faces.new((center_verts[iv], center_verts[iv + 1], outer[iv + 1][0], outer[iv][0]))
            bm.faces.new((outer[iv][seg_u], outer[iv + 1][seg_u], center_verts[iv + 1], center_verts[iv]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    if mat:
        obj.data.materials.append(mat)

    obj.shape_key_add(name="Basis", from_mix=False)
    sk_true = obj.shape_key_add(name="TrueScale", from_mix=False)

    span_edu = max(r_edu_out - r_edu_in, 1e-5)
    for i, v in enumerate(mesh.vertices):
        co = v.co
        dist = co.length
        if dist < 1e-5:
            sk_true.data[i].co = co.copy()
        else:
            t = max(0.0, min(1.0, (dist - r_edu_in) / span_edu))
            new_r = r_true_in + t * (r_true_out - r_true_in)
            sk_true.data[i].co = co.normalized() * new_r

    return obj


def add_anchor(name, location):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0.2
    empty.location = location
    bpy.context.collection.objects.link(empty)
    return empty


def build(filepath):
    clear_scene()

    mat_crust = make_material(
        "Mat_Crust",
        base_rgba=(0.16, 0.52, 0.82, 1.0),
        roughness=0.55,
        metallic=0.05,
    )
    mat_mantle = make_material(
        "Mat_Mantle",
        base_rgba=(0.88, 0.28, 0.06, 1.0),
        roughness=0.45,
        metallic=0.0,
        emission_rgba=(0.95, 0.25, 0.02, 1.0),
        emission_strength=0.45,
    )
    mat_core = make_material(
        "Mat_Core",
        base_rgba=(1.0, 0.82, 0.22, 1.0),
        roughness=0.22,
        metallic=0.88,
        emission_rgba=(1.0, 0.68, 0.12, 1.0),
        emission_strength=0.85,
    )

    create_cutaway_shell("Layer_Core", 0.0, 0.85, 0.0, 1.09, mat=mat_core)
    create_cutaway_shell("Layer_Mantle", 0.86, 1.72, 1.10, 1.96, mat=mat_mantle)
    create_cutaway_shell("Layer_Crust", 1.73, 2.00, 1.965, 2.00, mat=mat_crust)

    add_anchor("anchor_core", (0.38, 0.38, 0.15))
    add_anchor("anchor_mantle", (0.95, 0.95, 0.35))
    add_anchor("anchor_crust", (1.42, 1.42, 0.55))

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_yup=True,
        export_morph=True,
    )
