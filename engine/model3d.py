"""AI Doxtir — 3D sahna quruvchilari (Blender bpy, Cycles CPU).

Ishlatish (bitta asset):
    python -m engine.model3d '<asset_json>' out.png QUALITY
asset_json: {"build": "section|wisdom|front|implant_parts|molar|sprite", "params": {...}, "turn": {...}?}
Natija: out.png (shaffof fon) + out.json (ankerlar ekran koordinatalari).
QUALITY: preview | full
"""
import sys, math, json, random
import bpy, bmesh
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view

# ------------------------------------------------------------------ setup
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def scene(): return bpy.context.scene
def col(): return bpy.context.scene.collection

def srgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

_MATS = {}
def mat(name, color, rough=0.4, sss=0.0, emit=0.0, coat=0.0, metal=0.0, noise=None, alpha=1.0, transmission=0.0):
    key = (name, color, rough, sss, emit, coat, metal, noise, alpha, transmission)
    if key in _MATS: return _MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Subsurface Weight", "Subsurface"):
        if k in b.inputs: b.inputs[k].default_value = sss; break
    if "Subsurface Radius" in b.inputs: b.inputs["Subsurface Radius"].default_value = (0.08, 0.05, 0.04)
    for k in ("Coat Weight", "Clearcoat"):
        if k in b.inputs: b.inputs[k].default_value = coat; break
    for k in ("Transmission Weight", "Transmission"):
        if k in b.inputs: b.inputs[k].default_value = transmission; break
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if emit > 0:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs: b.inputs[k].default_value = (*srgb(color), 1); break
        if "Emission Strength" in b.inputs: b.inputs["Emission Strength"].default_value = emit
    if noise:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise; bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.3
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _MATS[key] = m
    return m

def M():
    return dict(
        ENAMEL=mat("enamel", "#f7f8fb", 0.18, sss=0.15, coat=0.6),
        DENTIN=mat("dentin", "#f1dcae", 0.45, sss=0.1),
        ROOTC=mat("root", "#ecd7a6", 0.5, sss=0.1),
        PULP=mat("pulp", "#e8606b", 0.35, sss=0.3, emit=0.15),
        PULP_HOT=mat("pulphot", "#ff1f3a", 0.3, sss=0.2, emit=3.5),
        GUTTA=mat("gutta", "#ef8a3c", 0.4, emit=0.3),
        GUM=mat("gum", "#f08fa0", 0.35, sss=0.35, noise=6),
        GUM_RED=mat("gumred", "#e2425a", 0.3, sss=0.3, noise=6, emit=0.25),
        BONE=mat("bone", "#efe3cf", 0.8, noise=14),
        CAR_OUT=mat("car_out", "#b07a3c", 0.6), CAR_IN=mat("car_in", "#3b2416", 0.7),
        FILL=mat("fill", "#eaf4f7", 0.15, coat=0.8), FILL_RIM=mat("fillrim", "#19b3a6", 0.3, emit=0.8),
        TARTAR=mat("tartar", "#cfa64a", 0.85, noise=30), PLAQUE=mat("plaque", "#efe08a", 0.7, noise=25, sss=0.2),
        METAL=mat("metal", "#b9c2c9", 0.22, metal=1.0), TITAN=mat("titan", "#9aa6b0", 0.3, metal=1.0, noise=60),
        ABSC=mat("absc", "#8f1020", 0.5, emit=1.2), GEL=mat("gel", "#7fd3ff", 0.05, alpha=0.45, transmission=0.6),
        YELLOW=mat("yel", "#ecd496", 0.25, sss=0.15, coat=0.4),
    )

# ------------------------------------------------------------------ primitives
def metaball(name, elems, res=0.035):
    mb = bpy.data.metaballs.new(name); mb.resolution = res; mb.render_resolution = res; mb.threshold = 0.6
    for (co, r) in elems:
        e = mb.elements.new(type="BALL"); e.co = co; e.radius = r
    ob = bpy.data.objects.new(name, mb); col().objects.link(ob)
    return ob

def to_mesh(ob, material):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    nob = bpy.data.objects.new(ob.name + "_m", me); col().objects.link(nob)
    bpy.data.objects.remove(ob)
    me.materials.append(material)
    for p in me.polygons: p.use_smooth = True
    return nob

def mb_mesh(name, elems, material, res=0.035):
    return to_mesh(metaball(name, elems, res), material)

def sphere(x, y, z, r, m, sx=1.0, sy=1.0, sz=1.0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("s", me); col().objects.link(ob); me.materials.append(m); ob.location = (x, y, z)
    for p in me.polygons: p.use_smooth = True
    return ob

def cyl(x, y, z1, z2, r, m, r2=None, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=z2 - z1)
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("c", me); col().objects.link(ob); me.materials.append(m); ob.location = (x, y, (z1 + z2) / 2)
    for p in me.polygons: p.use_smooth = True
    return ob

def box(x1, y1, z1, x2, y2, z2, m, bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(x2 - x1, y2 - y1, z2 - z1), verts=bm.verts)
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("b", me); col().objects.link(ob); me.materials.append(m)
    ob.location = ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)
    if bevel:
        md = ob.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 3
    return ob

def cutter(xmin):
    c = box(xmin, -10, -10, xmin + 10, 10, 10, mat("cut", "#ffffff"))
    c.hide_render = True; c.display_type = "WIRE"
    return c

def cut(ob, xmin):
    md = ob.modifiers.new("cut", "BOOLEAN"); md.object = cutter(xmin); md.operation = "DIFFERENCE"
    try: md.solver = "EXACT"
    except Exception: pass

def subtract(ob, other):
    md = ob.modifiers.new("sub", "BOOLEAN"); md.object = other; md.operation = "DIFFERENCE"
    try: md.solver = "EXACT"
    except Exception: pass

def stain(points, m, x=0.034):
    """flat organic region on the section plane: points = [(y, z, r)]"""
    ob = mb_mesh("stain", [((0, y, z), r) for (y, z, r) in points], m, 0.02)
    ob.scale = (0.001, 1, 1); ob.location.x = x
    return ob

def chain(p0, p1, r0, r1, n=10, s=1.0):
    return [((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t), (r0 + (r1 - r0) * t) * s)
            for t in [i / (n - 1) for i in range(n)]]

# ------------------------------------------------------------------ molar (same proportions as karies pilot)
def crown_elems(s=1.0, cusp=1.0, dz=0.0, oy=0.0, oz=0.0):
    el = [((0, oy, 0.42 + dz + oz), 0.62 * s)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            el.append(((sx * 0.3 * s, oy + sy * 0.27 * s, 0.45 + dz + oz), 0.5 * s))
            el.append(((sx * 0.31 * s, oy + sy * 0.28 * s, 0.74 + dz + oz), 0.33 * s * cusp))
    return el

def molar(mm, oy=0.0, oz=0.0, scale=1.0, enamel_scale=1.0, den_scale=0.78, root_len=1.0, pulp="normal",
          enamel_mat=None, spot=False, with_roots=True):
    """Returns dict of meshes (body, enamel, den, pulp) positioned at (0, oy, oz)."""
    s = scale; L = root_len
    def R(p0, p1, r0, r1, n=9, k=1.0):
        return chain((p0[0] * s, oy + p0[1] * s, oz + p0[2] * s), (p1[0] * s, oy + p1[1] * s, oz + p1[2] * s), r0 * s, r1 * s, n, k)
    body = [((x * s, oy + y * s, oz + z * s), r * s) for ((x, y, z), r) in crown_elems(0.97)] + [((0, oy, oz + 0.08 * s), 0.6 * s)]
    if with_roots:
        body += R((0, -0.24, 0.05), (0, -0.42, 0.05 - 1.3 * L), 0.42, 0.16)
        body += R((0, 0.24, 0.05), (0, 0.40, 0.05 - 1.25 * L), 0.42, 0.16)
        body += R((-0.2, 0, 0.05), (-0.4, 0.0, 0.05 - 1.1 * L), 0.36, 0.14)
    o = {}
    o["body"] = mb_mesh("body", body, mm["ROOTC"])
    o["enamel"] = mb_mesh("enamel", [((x * s, oy + y * s, oz + z * s), r * s) for ((x, y, z), r) in crown_elems(enamel_scale)], enamel_mat or mm["ENAMEL"])
    den = [((x * s, oy + y * s, oz + z * s), r * s) for ((x, y, z), r) in crown_elems(den_scale, 0.7, -0.03)] + [((0, oy, oz + 0.08 * s), 0.52 * s)]
    if with_roots:
        den += R((0, -0.24, 0.05), (0, -0.42, 0.05 - 1.27 * L), 0.36, 0.12)
        den += R((0, 0.24, 0.05), (0, 0.40, 0.05 - 1.22 * L), 0.36, 0.12)
    o["den"] = mb_mesh("den", den, mm["DENTIN"])
    if pulp != "none":
        pl = [((0, oy, oz + 0.27 * s), 0.29 * s)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                pl.append(((sx * 0.14 * s, oy + sy * 0.13 * s, oz + 0.38 * s), 0.15 * s))
        if with_roots:
            pl += R((0, -0.17, 0.15), (0, -0.4, 0.15 - 1.28 * L), 0.15, 0.06, 22)
            pl += R((0, 0.17, 0.15), (0, 0.38, 0.15 - 1.23 * L), 0.15, 0.06, 22)
        pm = {"normal": mm["PULP"], "hot": mm["PULP_HOT"], "gutta": mm["GUTTA"]}.get(pulp, mm["PULP"])
        o["pulp"] = mb_mesh("pulp", pl, pm, 0.025)
    if spot:
        o["spot"] = sphere(0.06 * s, oy + 0.04 * s, oz + 0.93 * s, 0.09 * s, mm["CAR_IN"], sz=0.5)
    return o

def section_cut(objs):
    order = [("body", 0.0), ("enamel", 0.008), ("den", 0.016), ("pulp", 0.024)]
    for k, x in order:
        if k in objs: cut(objs[k], x)

def jaw(mm, gum_z=0.0, gum_mat=None, bone_drop=0.0, width=1.1, gum_r=0.5):
    ys = [i * 0.55 for i in range(-int(width / 0.55) - 1, int(width / 0.55) + 2)]
    gum = mb_mesh("gum", [((x, y, gum_z), gum_r) for x in (-0.9, -0.45, 0.0, 0.45) for y in ys], gum_mat or mm["GUM"])
    bone = mb_mesh("bone", [((x, y, z - bone_drop), 0.58) for x in (-0.9, -0.45, 0.0, 0.45) for y in ys for z in (-0.45, -0.9, -1.35)], mm["BONE"])
    cut(gum, -0.02); cut(bone, -0.03)
    return gum, bone

# caries stain shapes on the section plane (y, z, r)
S1 = [(0.0, 0.735, 0.07), (0.0, 0.70, 0.06)]
S2 = [(0.0, 0.735, 0.09), (0.0, 0.68, 0.1), (0.0, 0.62, 0.12), (-0.06, 0.585, 0.11), (0.06, 0.585, 0.11)]
S3 = S2 + [(0.0, 0.54, 0.13), (-0.03, 0.49, 0.12), (0.03, 0.47, 0.1)]

# ------------------------------------------------------------------ builders
ANCH = {}

def build_section(p):
    mm = M()
    caries = p.get("caries", 0); fill = p.get("fill", False)
    gum_mode = p.get("gum", "normal")
    gum_z = {"normal": 0.0, "red": 0.04, "recede": -0.28}[gum_mode]
    if p.get("baby"):
        o = molar(mm, oz=0.22, scale=0.72, root_len=0.75, pulp=p.get("pulp", "normal"))
    elif p.get("no_tooth"):
        o = {}
    else:
        en_s = p.get("enamel_scale", 1.0)
        o = molar(mm, pulp=p.get("pulp", "normal"), enamel_scale=en_s, den_scale=p.get("den_scale", 0.78),
                  enamel_mat=mm["YELLOW"] if p.get("yellow") else None)
    if p.get("access") and o:
        hole = sphere(0, 0, 0.86, 0.2, mm["CAR_IN"], sz=1.4); hole.hide_render = True
        for k in ("enamel", "den", "body"): subtract(o[k], hole)
    section_cut(o)
    jaw(mm, gum_z=gum_z, gum_mat=mm["GUM_RED"] if gum_mode in ("red",) or p.get("gum_red") else None,
        bone_drop=p.get("bone_drop", 0.0), gum_r=0.56 if gum_mode == "red" else 0.5)
    X = 0.034
    bs, boz = (0.72, 0.22) if p.get("baby") else (1.0, 0.0)
    def T(pts): return [(y * bs, z * bs + boz, r * bs) for (y, z, r) in pts]
    if caries:
        shape = T({1: S1, 2: S2, 3: S3}[caries])
        if fill:
            stain(shape, mm["FILL_RIM"], X); stain([(y, z, r * 0.84) for (y, z, r) in shape], mm["FILL"], X + 0.004)
        else:
            stain(shape, mm["CAR_OUT"], X); stain([(y, z, r * 0.66) for (y, z, r) in shape], mm["CAR_IN"], X + 0.004)
    if p.get("access_fill"):
        stain([(0, 0.8, 0.16), (0, 0.65, 0.18), (0, 0.5, 0.2)], mm["FILL_RIM"], X)
        stain([(0, 0.8, 0.13), (0, 0.65, 0.15), (0, 0.5, 0.17)], mm["FILL"], X + 0.004)
    t = p.get("tartar", 0)
    if t:
        rnd = random.Random(4)
        for sy in (-1, 1):
            pts = [(sy * (0.5 + rnd.uniform(-0.03, 0.04)), z, rnd.uniform(0.05, 0.08) * (1 + 0.4 * (t - 1)))
                   for z in [0.24, 0.16, 0.08, 0.0][: 2 + t]]
            stain(pts, mm["TARTAR"] if t >= 2 else mm["PLAQUE"], 0.05)
            for (yy, zz, rr) in pts:   # 3D crust visible on tooth outside
                sphere(-0.15, yy * 1.03, zz, rr * 0.9, mm["TARTAR"] if t >= 2 else mm["PLAQUE"], sx=1.6)
    if p.get("abscess"):
        stain([(-0.42, -1.25, 0.16), (-0.42, -1.12, 0.12)], mm["ABSC"], 0.045)
        stain([(0.40, -1.2, 0.16), (0.40, -1.08, 0.12)], mm["ABSC"], 0.045)
    if p.get("files"):
        for (y0, y1) in ((-0.2, -0.36), (0.2, 0.34)):
            ob = cyl(0, 0, -0.55, 0.55, 0.018, mm["METAL"]); ob.location = (0.06, (y0 + y1) / 2 + (y0 - y1) * 0.6, 0.55)
            ob.rotation_euler = (math.atan2(y1 - y0, 1.0) * (-1 if y0 < 0 else -1), 0, 0)
            # handle
            h = cyl(0, 0, 0, 0.22, 0.07, mat("hdl", "#ffd24a" if y0 < 0 else "#e83e5a", 0.4))
            h.location = (0.06, ob.location.y - (y1 - y0) * 0.55, 1.18)
    if p.get("germ"):   # permanent tooth germ under baby tooth
        g = molar(mm, oz=-0.95, scale=0.8, with_roots=False, pulp="normal")
        section_cut(g)
    if p.get("germ_glow"):
        stain([(0, -0.25, 0.22), (0, -0.4, 0.2)], mm["ABSC"], 0.05)
    impl = p.get("implant")
    if impl:
        screw(mm, top=-0.02)
        if impl in ("abutment", "crown"): cyl(0, 0, -0.02, 0.32, 0.17, mm["TITAN"], r2=0.13)
        if impl == "crown":
            c = mb_mesh("crown", crown_elems(1.0, 1.0, -0.06), mm["ENAMEL"])
        if impl == "screw":   # gum opened
            pass
    # anchors (3D, in section plane x≈0.03)
    tooth_pts = {"enamel": (-0.47, 0.5), "dentin": (-0.2, 0.05), "pulp": (0.0, 0.27), "canal": (0.3, -0.6),
                 "car1": (0.0, 0.72), "car2": (0.0, 0.62), "car3": (0.0, 0.52), "top": (0.0, 0.85), "crown": (0.0, 0.5), "root_tip": (0.0, -1.3)}
    for k, (yy, zz) in tooth_pts.items(): ANCH[k] = (0.03, yy * bs, zz * bs + boz)
    ANCH.update({"gum": (0.0, -0.85, 0.15), "bone": (0.0, -0.8, -0.8), "tartar_l": (0.05, -0.52, 0.12), "tartar_r": (0.05, 0.52, 0.12),
                 "apex_l": (0.03, -0.42, -1.2), "apex_r": (0.03, 0.40, -1.15), "germ": (0.03, 0.0, -0.55), "implant": (0.2, 0.0, -0.5),
                 "abut": (0.2, 0.0, 0.15)})
    lights(); setup(1080, 1500)
    camera((5.0, -2.3, 0.9), (0, 0, -0.25), 50)

def screw(mm, top=0.0, length=1.15, r=0.22, x=0.0, y=0.0):
    n = 11; step = length / n
    for i in range(n):
        z1 = top - (i + 1) * step; z2 = top - i * step
        rr = r * (1 - 0.35 * (i / n) ** 2)
        cyl(x, y, z1, z1 + step * 0.55, rr * 0.78, mm["TITAN"], r2=rr, seg=40)
        cyl(x, y, z1 + step * 0.55, z2, rr, mm["TITAN"], r2=rr * 0.78, seg=40)
    cyl(x, y, top - length - 0.08, top - length, r * 0.45, mm["TITAN"], r2=r * 0.6)

def build_wisdom(p):
    mm = M(); st = p.get("stage", 0)
    a = molar(mm, oy=-0.75)
    section_cut(a)
    if st < 2:
        w = molar(mm, oy=0.0, oz=0.0)
        root = bpy.data.objects.new("w", None); col().objects.link(root)
        for o in w.values(): o.parent = root
        root.location = (0, 0.62, -0.42); root.rotation_euler = (math.radians(38), 0, 0)
        section_cut(w)
    ys = [-2.2, -1.65, -1.1, -0.55, 0.0, 0.55, 1.1, 1.65]
    gm = mm["GUM_RED"] if st == 1 else mm["GUM"]
    gum = mb_mesh("gum", [((x, y, 0.0 if y < 0.3 else 0.12), 0.5) for x in (-0.9, -0.45, 0.0, 0.45) for y in ys], gm)
    bone = mb_mesh("bone", [((x, y, z), 0.58) for x in (-0.9, -0.45, 0.0, 0.45) for y in ys for z in (-0.45, -0.9, -1.35)], mm["BONE"])
    if st == 2:
        hole = sphere(0, 0.65, -0.6, 0.45, mm["BONE"], sy=0.8, sz=1.3); hole.hide_render = True
        subtract(bone, hole); subtract(gum, hole)
    cut(gum, -0.02); cut(bone, -0.03)
    if st == 1:
        stain([(0.35, 0.12, 0.14), (0.5, 0.05, 0.12)], mm["ABSC"], 0.05)
    ANCH.update({"wisdom": (0.03, 0.62, -0.1), "neighbor": (0.03, -0.75, 0.5), "contact": (0.03, 0.05, 0.1), "gum": (0.0, 0.7, 0.2),
                 "socket": (0.03, 0.65, -0.5)})
    lights(); setup(1080, 1500)
    camera((6.2, -1.6, 0.8), (0, -0.05, -0.3), 46)

def incisor(mm, x, y, rot=0.0, tilt=0.0, w=0.85, h=1.05, pointed=False, dz=0.0, enamel=None, root_show=False):
    """upper tooth, crown hanging down from gum line z=0"""
    el = []
    for i in range(7):
        t = i / 6
        el.append(((0, 0, -0.08 - t * (h - 0.2)), (0.33 + 0.07 * math.sin(t * math.pi)) * w / 0.85))
    for sx in (-1, 1):
        for i in range(5):
            t = i / 4
            el.append(((sx * 0.2 * w / 0.85, 0, -0.15 - t * (h - 0.35)), 0.24 * w / 0.85))
    root = chain((0, 0.04, 0.05), (0, 0.08, 0.55), 0.3, 0.16, 6)
    ob = mb_mesh("inc", el, enamel or mm["ENAMEL"])
    rt = mb_mesh("root", root, mm["ROOTC"])
    for o in (ob, rt):
        o.scale = (1, 0.55, 1)
        o.rotation_euler = (math.radians(tilt), 0, math.radians(rot))
        o.location = (x, y, dz)
    return ob

ROW = [(-1.95, "c"), (-1.25, "l"), (-0.45, "i"), (0.45, "i"), (1.25, "l"), (1.95, "c")]

def build_front(p):
    mm = M(); crook = p.get("crooked", 0.0)
    enamel = mm["YELLOW"] if p.get("yellow") else (mat("en_w", "#ffffff", 0.12, sss=0.1, coat=0.8) if p.get("white") else mm["ENAMEL"])
    rnd = random.Random(11)
    offs = [(0.12, -0.18, 14, 0.06), (-0.05, 0.22, -18, -0.08), (0.06, -0.1, 9, 0.0), (-0.1, 0.16, -12, 0.05), (0.08, -0.22, 20, -0.05), (-0.06, 0.12, -10, 0.1)]
    teeth = []
    for i, (x, kind) in enumerate(ROW):
        dx, dy, rot, dz = offs[i]
        w = {"c": 0.94, "l": 0.84, "i": 1.04}[kind]; h = {"c": 1.12, "l": 0.94, "i": 1.1}[kind]
        y = 0.16 * x * x
        teeth.append((x + dx * crook, y + dy * crook, rot * crook - x * 14, dz * crook))
        incisor(mm, x + dx * crook, y + dy * crook, rot=rot * crook - x * 14, tilt=-8, w=w, h=h, pointed=(kind == "c"), dz=dz * crook, enamel=enamel)
        if p.get("gel"):
            g = incisor(mm, x + dx * crook, y + dy * crook - 0.01, rot=rot * crook - x * 14, tilt=-8, w=w * 1.08, h=h * 1.03, pointed=(kind == "c"), dz=dz * crook, enamel=mm["GEL"])
        if p.get("plaque"):
            for k in range(9):
                sphere(x + dx * crook + (k - 4) * 0.075 * w, y + dy * crook - 0.17, -0.13 - 0.05 * (k % 3), 0.065, mm["PLAQUE"], sy=0.3)
        if p.get("brackets"):
            box(x + dx * crook - 0.13, y + dy * crook - 0.32, -0.62, x + dx * crook + 0.13, y + dy * crook - 0.2, -0.38, mm["METAL"], 0.02)
    if p.get("brackets"):
        pts = [(tx, ty - 0.33, -0.5 + tz) for (tx, ty, _, tz) in teeth]
        cu = bpy.data.curves.new("wire", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.02
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
        for i, q in enumerate(pts): sp.points[i].co = (*q, 1)
        sp.use_smooth = True
        wo = bpy.data.objects.new("wire", cu); col().objects.link(wo); cu.materials.append(mm["METAL"])
    gz = 0.22 if p.get("recession") else 0.0
    gm = mm["GUM_RED"] if p.get("gum_red") else mm["GUM"]
    gel = []
    for i in range(-5, 6):
        x = i * 0.42; y = 0.16 * x * x
        gel.append(((x, y + 0.05, 0.3 + gz), 0.55))
        gel.append(((x, y - 0.05, 0.05 + gz + 0.08 * abs(math.sin(i * 1.6))), 0.32))
        gel.append(((x, y + 0.35, 0.55 + gz), 0.6))
        gel.append(((x, y + 0.1, 0.75 + gz), 0.6))
    mb_mesh("gumrow", gel, gm)
    if p.get("recession"):
        for (tx, ty, _, tz) in teeth:
            sphere(tx, ty - 0.05, 0.12, 0.25, mm["ROOTC"], sy=0.5, sz=0.75)
    ANCH.update({"center": (0, -0.2, -0.5), "gumline": (0.45, -0.25, 0.0), "tooth2": (-1.25, 0.0, -0.5), "edge": (0, -0.2, -1.05),
                 "left": (-1.6, 0, -0.4), "right": (1.6, 0, -0.4)})
    lights(); setup(1080, 1100)
    camera((0, -6.2, -0.55), (0, 0.4, -0.45), 50)

def build_molar(p):
    mm = M()
    o = molar(mm, spot=p.get("spot", False), enamel_mat=mm["YELLOW"] if p.get("yellow") else None)
    root = bpy.data.objects.new("root", None); col().objects.link(root)
    for ob in o.values(): ob.parent = root
    if p.get("tartar"):
        for k in range(14):
            a = k / 14 * math.tau
            s = sphere(math.cos(a) * 0.52, math.sin(a) * 0.5, 0.08 + 0.05 * math.sin(k * 2.1), 0.08, mm["TARTAR"]); s.parent = root
    ANCH.update({"top": (0.06, 0.04, 0.93), "crown": (0, 0, 0.5)})
    lights(); setup(900, 1080)
    camera((0, -5.2, 1.2), (0, 0, -0.1), 50)
    return root

def build_implant_parts(p):
    mm = M()
    root = bpy.data.objects.new("root", None); col().objects.link(root)
    before = set(bpy.data.objects)
    screw(mm, top=-0.25)
    cyl(0, 0, 0.0, 0.34, 0.17, mm["TITAN"], r2=0.13)
    mb_mesh("crown", crown_elems(1.0, 1.0, 0.2), mm["ENAMEL"])
    for ob in set(bpy.data.objects) - before:
        if ob.parent is None and ob != root: ob.parent = root
    ANCH.update({"crown": (0, 0, 0.8), "abut": (0, 0, 0.17), "screw": (0, 0, -0.8)})
    lights(); setup(900, 1080)
    camera((0, -5.0, 0.6), (0, 0, -0.2), 46)
    return root

def build_sprite(p):
    mm = M(); kind = p["kind"]
    if kind in ("bact_g", "bact_p"):
        BODY = mat("bb" + kind, {"bact_g": "#6cc04a", "bact_p": "#a66bd9"}[kind], 0.35, sss=0.2, noise=9)
        sphere(0, 0, 0, 0.5, BODY, sx=1.15, sz=0.85)
        for i in range(12):
            a = i * math.tau / 12; e = math.radians(-20 + (i % 3) * 25)
            x, y, z = math.cos(a) * math.cos(e) * 0.55, math.sin(a) * math.cos(e) * 0.5, math.sin(e) * 0.42
            if y < -0.2: continue
            sphere(x, y, z, 0.08, BODY)
        W_ = mat("w", "#ffffff", 0.2); K_ = mat("k", "#151515", 0.1)
        for sx in (-1, 1):
            sphere(sx * 0.17, -0.38, 0.12, 0.13, W_); sphere(sx * 0.19, -0.49, 0.1, 0.06, K_)
            b = sphere(sx * 0.17, -0.44, 0.3, 0.12, mat("br", "#2b2b2b", 0.5), sz=0.25); b.rotation_euler = (0, -sx * math.radians(28), 0)
        sphere(0, -0.43, -0.12, 0.09, mat("m", "#5a1d1d", 0.5), sx=1.5, sz=0.45)
        cam = ((0, -3.4, 0.5), (0, 0, 0), 50); size = (600, 600)
    elif kind == "sugar":
        b = box(-0.4, -0.4, -0.4, 0.4, 0.4, 0.4, mat("sug", "#ffffff", 0.25, sss=0.3, noise=40), 0.08)
        b.rotation_euler = (math.radians(20), math.radians(10), math.radians(35))
        cam = ((0, -3.2, 0.9), (0, 0, 0), 50); size = (500, 500)
    elif kind == "soda":
        c = cyl(0, 0, -0.6, 0.6, 0.33, mat("can", "#e23b3b", 0.3, metal=0.4))
        cyl(0, 0, 0.6, 0.66, 0.3, mm["METAL"], r2=0.27); cyl(0, 0, -0.66, -0.6, 0.27, mm["METAL"], r2=0.3)
        cyl(0, 0, -0.12, 0.12, 0.335, mat("band", "#ffffff", 0.3))
        for i in range(6): sphere(0.5 + 0.12 * (i % 2), -0.1, 0.8 + i * 0.16, 0.05, mat("bub", "#bfe9ff", 0.05, alpha=0.6, transmission=0.8))
        root = bpy.data.objects.new("r", None)
        cam = ((0.3, -3.6, 0.6), (0, 0, 0.05), 50); size = (500, 600)
    elif kind == "lemon":
        sphere(0, 0, 0, 0.45, mat("lem", "#ffd23f", 0.4, sss=0.2, noise=25), sx=1.3)
        sphere(0.6, 0, 0, 0.1, mat("lem2", "#e9bf22", 0.4)); sphere(-0.6, 0, 0, 0.1, mat("lem2", "#e9bf22", 0.4))
        cam = ((0, -3.2, 0.8), (0, 0, 0), 50); size = (500, 500)
    elif kind == "brush":
        box(-1.6, -0.08, -0.06, 0.4, 0.08, 0.06, mat("hd", "#12a89a", 0.3), 0.05)
        box(0.4, -0.1, -0.05, 1.05, 0.1, 0.06, mat("hd2", "#e9f6f5", 0.3), 0.04)
        for i in range(8):
            for j in range(3):
                cyl(0.47 + i * 0.075, -0.06 + j * 0.06, 0.06, 0.32, 0.022, mat("bri", "#ffffff" if (i + j) % 2 else "#7fd3ff", 0.5), seg=8)
        cam = ((0, -3.6, 0.9), (-0.2, 0, 0.05), 40); size = (800, 400)
    elif kind == "candy":
        sphere(0, 0, 0.45, 0.36, mat("cd", "#ff5c8a", 0.2, coat=0.8), sy=0.4)
        cyl(0, 0, -0.7, 0.2, 0.04, mat("st", "#ffffff", 0.4))
        cam = ((0, -3.2, 0.3), (0, 0, 0.05), 50); size = (500, 600)
    lights(1.1); setup(*size)
    camera(*cam)

BUILDERS = {"section": build_section, "wisdom": build_wisdom, "front": build_front, "molar": build_molar,
            "implant_parts": build_implant_parts, "sprite": build_sprite}
from engine import olmaliq3d as _olm  # @ai_olmaliq quruvchilari
_olm.register(sys.modules[__name__]); BUILDERS.update(_olm.BUILDERS)

# ------------------------------------------------------------------ lighting / render
CAM = {}
def lights(strength=1.0):
    w = bpy.data.worlds.new("w"); scene().world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#eaf6f7"), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    for (loc, en, size, colr) in [((3, -3, 4), 900, 4, "#ffffff"), ((-4, 2, 2), 350, 5, "#cfefff"), ((0, 4, -1), 250, 4, "#ffe9e0")]:
        L = bpy.data.lights.new("a", "AREA"); L.energy = en * strength; L.size = size; L.color = srgb(colr)
        o = bpy.data.objects.new("a", L); col().objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

def camera(loc, tgt, lens=50):
    cam = bpy.data.cameras.new("c"); cam.lens = lens
    co = bpy.data.objects.new("c", cam); col().objects.link(co); scene().camera = co
    co.location = loc; co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM["obj"] = co
    return co

SIZE = {}
def setup(w, h):
    s = scene(); SIZE["w"], SIZE["h"] = w, h
    s.render.engine = "CYCLES"; s.cycles.device = "CPU"; s.cycles.use_denoising = True; s.cycles.max_bounces = 6
    s.render.resolution_x = w; s.render.resolution_y = h; s.render.film_transparent = True
    s.render.image_settings.file_format = "PNG"; s.render.image_settings.color_mode = "RGBA"
    s.view_settings.view_transform = "AgX"
    try: s.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass

def project_anchors():
    s = scene(); bpy.context.view_layer.update(); out = {}
    for k, p in ANCH.items():
        v = world_to_camera_view(s, CAM["obj"], Vector(p))
        out[k] = [round(v.x * SIZE["w"], 1), round((1 - v.y) * SIZE["h"], 1)]
    return out

def render_asset(spec, out_png, quality="full"):
    reset(); _MATS.clear(); ANCH.clear(); CAM.clear(); SIZE.clear()
    root = BUILDERS[spec["build"]](spec.get("params", {}))
    s = scene()
    samples = {"full": spec.get("samples", 32), "preview": 6}[quality]
    s.cycles.samples = samples
    if quality == "preview":
        s.render.resolution_percentage = 50
    turn = spec.get("turn")
    if turn:
        if root is None:
            root = bpy.data.objects.new("root", None); col().objects.link(root)
            for ob in list(s.objects):
                if ob.type in ("MESH", "META", "CURVE") and ob.parent is None: ob.parent = root
        n = turn.get("frames", 24) if quality == "full" else 3
        a0, a1 = turn.get("from", -40), turn.get("to", 120)
        if quality == "full": s.cycles.samples = spec.get("turn_samples", 12)
        for f in range(n):
            t = f / max(1, n - 1)
            root.rotation_euler = (math.radians(turn.get("tilt", 12)), 0, math.radians(a0 + (a1 - a0) * t))
            s.render.filepath = out_png.replace(".png", f"_{f:03d}.png")
            bpy.ops.render.render(write_still=True)
        json.dump({"frames": n, "size": [SIZE["w"], SIZE["h"]], "anchors": {}}, open(out_png.replace(".png", ".json"), "w"))
        return
    s.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    json.dump({"size": [SIZE["w"], SIZE["h"]], "anchors": project_anchors()}, open(out_png.replace(".png", ".json"), "w"))

if __name__ == "__main__":
    spec = json.loads(sys.argv[1]); out = sys.argv[2]; q = sys.argv[3] if len(sys.argv) > 3 else "full"
    render_asset(spec, out, q)
    print("ASSET_OK", out)
