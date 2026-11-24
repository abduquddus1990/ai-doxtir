"""@ai_olmaliq — 3D sahna quruvchilari (Blender bpy). engine/model3d.py ichidan ro'yxatga olinadi.

Quruvchilar (asset "build" qiymati) va parametrlari:
  terrain   — vodiy dioramasi: Qurama tog'lari, daryo, olmazor, shahar.
              params: mountains(bool=True) snow(bool=True) river(bool=True) trees(int=0) apples(bool=True)
                      city(0..1=0) future(bool) pin(bool) seed(int)
              anchors: center, mountain, river, city, orchard, pin
  quarry    — ochiq karyer (pog'onali chuqurlik). params: levels(int=7) trucks(int=3) water(bool=True)
              anchors: center, bottom, rim, bench, truck
  ore       — ruda bo'lagi. params: split(0..1=0) metals(int=13)
              anchors: center, m0..m12 (metall belgilari, faqat split>0)
  flotation — flotatsiya tanki. params: bubbles(int=40) loaded(bool=True)
              anchors: tank, froth, bubble, bottom
  globe     — Yer shari, Olmaliq belgisi. params: arcs(int=0) spin(gradus=0)
              anchors: center, olmaliq, a0..a5 (yoy uchlari)
  shaft     — yer osti kesimi: minora, lift, tunnel. params: cage(0..1=0.5 lift chuqurligi) miner(bool=True)
              anchors: surface, headframe, cage, tunnel, miner, vein
  osprite   — kichik obyekt. params: kind = apple|truck|cathode|wire|gold|silver|helmet|phone|nugget
"""
import math, random, os
import bpy
from mathutils import Vector, Matrix, noise

G = None  # engine.model3d moduli (register orqali)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def register(mod):
    global G
    G = mod

# ------------------------------------------------------------------ helpers
def fbm(x, y, oct=4, seed=0):
    s, a, f = 0.0, 1.0, 1.0
    for _ in range(oct):
        s += a * noise.noise(Vector((x * f + seed * 13.1, y * f - seed * 7.3, 0.37 * seed)))
        a *= 0.5; f *= 2.03
    return s

def ramp_mat(name, stops, zmin, zmax, rough=0.8, bump=0.0, bump_scale=8.0, slope_shade=0.0):
    """balandlik (Z) bo'yicha rang: stops = [(0..1, '#hex'), ...]"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange"); cr = nt.nodes.new("ShaderNodeValToRGB")
    mr.inputs["From Min"].default_value = zmin; mr.inputs["From Max"].default_value = zmax
    nt.links.new(geo.outputs["Position"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], cr.inputs["Fac"])
    if slope_shade:
        sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sn.inputs[0])
        ms = nt.nodes.new("ShaderNodeMapRange"); ms.inputs["From Min"].default_value = 0.5; ms.inputs["From Max"].default_value = 0.95
        ms.inputs["To Min"].default_value = 1 - slope_shade; ms.inputs["To Max"].default_value = 1.0
        nt.links.new(sn.outputs["Z"], ms.inputs["Value"])
        vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "MULTIPLY"
        nt.links.new(cr.outputs["Color"], vm.inputs[0]); nt.links.new(ms.outputs["Result"], vm.inputs[1])
        nt.links.new(vm.outputs["Vector"], b.inputs["Base Color"])
    else:
        nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    els = cr.color_ramp.elements
    els[0].position = stops[0][0]; els[0].color = (*G.srgb(stops[0][1]), 1)
    els[1].position = stops[-1][0]; els[1].color = (*G.srgb(stops[-1][1]), 1)
    for pos, h in stops[1:-1]:
        e = els.new(pos); e.color = (*G.srgb(h), 1)
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = bump_scale; bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def polar_mesh(name, zf, R=4.0, NR=70, NS=160, skirt=0.7, mats=(), sx=1.0):
    """dumaloq diorama: zf(x, y) -> z. Chetida tuproq 'yubka'."""
    verts = [(0.0, 0.0, zf(0.0, 0.0))]; faces = []; fmat = []
    for i in range(1, NR + 1):
        r = R * i / NR
        for j in range(NS):
            a = j / NS * math.tau; x, y = r * math.cos(a) * sx, r * math.sin(a)
            verts.append((x, y, zf(x, y)))
    def vid(i, j): return 1 + (i - 1) * NS + (j % NS)
    for j in range(NS):
        faces.append((0, vid(1, j), vid(1, j + 1))); fmat.append(0)
    for i in range(1, NR):
        for j in range(NS):
            faces.append((vid(i, j), vid(i + 1, j), vid(i + 1, j + 1), vid(i, j + 1))); fmat.append(0)
    if skirt:
        base = len(verts)
        for j in range(NS):
            x, y, _ = verts[vid(NR, j)]; verts.append((x, y, -skirt))
        for j in range(NS):
            faces.append((vid(NR, j), base + j, base + (j + 1) % NS, vid(NR, j + 1))); fmat.append(1)
        faces.append(tuple(base + j for j in reversed(range(NS)))); fmat.append(1)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    for mt in mats: me.materials.append(mt)
    for k, p in enumerate(me.polygons):
        p.material_index = fmat[k] if len(mats) > 1 else 0; p.use_smooth = fmat[k] == 0
    ob = bpy.data.objects.new(name, me); G.col().objects.link(ob)
    return ob

def curve(points, m, bevel=0.02, name="cv"):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = bevel; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(points) - 1)
    for i, q in enumerate(points): sp.points[i].co = (*q, 1)
    ob = bpy.data.objects.new(name, cu); G.col().objects.link(ob); cu.materials.append(m)
    return ob

def ico(r, m, sub=4, rough=0.0, seed=0, loc=(0, 0, 0), sc=(1, 1, 1)):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts:
        n = v.co.normalized(); d = noise.noise(n * 2.2 + Vector((seed, seed * 0.7, 0))) * 0.6 + noise.noise(n * 5.0 + Vector((0, seed, 1))) * 0.25
        v.co = n * r * (1 + rough * d)
    me = bpy.data.meshes.new("ico"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("ico", me); G.col().objects.link(ob); me.materials.append(m)
    ob.location = loc; ob.scale = sc
    for p in me.polygons: p.use_smooth = True
    return ob

def look_cam(loc, tgt, lens, vivid=True):
    if vivid:  # AgX to'q ranglarni pastel qiladi — olmaliq sahnalari uchun Standard
        vs = G.scene().view_settings; vs.view_transform = "Standard"
        try: vs.look = "None"
        except Exception: pass
        vs.exposure = -0.35
    return G.camera(loc, tgt, lens)

# ------------------------------------------------------------------ props
def apple_tree(x, y, z, s, mats, apples=True, rnd=None):
    rnd = rnd or random.Random(1)
    G.cyl(x, y, z, z + 0.32 * s, 0.045 * s, mats["TRUNK"], r2=0.03 * s, seg=10)
    cz = z + 0.42 * s
    for k in range(3):
        G.sphere(x + (k - 1) * 0.08 * s, y + rnd.uniform(-0.05, 0.05) * s, cz + rnd.uniform(-0.03, 0.05) * s, 0.17 * s, mats["LEAF"])
    if apples:
        for k in range(6):
            a = rnd.uniform(0, math.tau); e = rnd.uniform(-0.4, 0.6)
            G.sphere(x + math.cos(a) * math.cos(e) * 0.2 * s, y + math.sin(a) * math.cos(e) * 0.18 * s - 0.03 * s, cz + math.sin(e) * 0.15 * s,
                     0.035 * s, mats["APPLE"])

def building(x, y, z, w, d, h, m, roof):
    G.box(x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, m, 0.01)
    G.box(x - w / 2 - 0.01, y - d / 2 - 0.01, z + h, x + w / 2 + 0.01, y + d / 2 + 0.01, z + h + 0.025, roof)

def truck(x, y, z, s, rot, mats):
    root = bpy.data.objects.new("truck", None); G.col().objects.link(root)
    parts = [G.box(-0.5, -0.22, 0.12, 0.25, 0.22, 0.42, mats["YEL"], 0.02), G.box(0.25, -0.2, 0.12, 0.5, 0.2, 0.36, mats["YEL"], 0.02),
             G.box(0.3, -0.19, 0.25, 0.48, 0.19, 0.34, mats["GLASS"], 0.01), G.box(-0.5, -0.23, 0.36, 0.2, 0.23, 0.46, mats["ORE"], 0.03)]
    for (wx, wy) in [(-0.3, -0.23), (-0.3, 0.23), (0.35, -0.23), (0.35, 0.23)]:
        w = G.cyl(0, 0, -0.04, 0.04, 0.11, mats["TIRE"], seg=16); w.rotation_euler = (math.pi / 2, 0, 0); w.location = (wx, wy, 0.11); parts.append(w)
    for p in parts: p.parent = root
    root.location = (x, y, z); root.scale = (s, s, s); root.rotation_euler = (0, 0, rot)
    return root

def common_mats():
    return dict(
        TRUNK=G.mat("trunk", "#7a5234", 0.8), LEAF=G.mat("leaf", "#4fa35a", 0.6, sss=0.1, noise=12), APPLE=G.mat("apple", "#e5383b", 0.3, coat=0.5),
        WALL=G.mat("wall", "#f7f2ea", 0.6), WALL2=G.mat("wall2", "#e8dccb", 0.6), ROOF=G.mat("roof", "#12a89a", 0.5), ROOF2=G.mat("roof2", "#b8673a", 0.5),
        GLASSB=G.mat("glassb", "#5fb6d9", 0.08, metal=0.3, coat=0.8), SOLAR=G.mat("solar", "#1d3a5f", 0.15, metal=0.4),
        WATER=G.mat("water", "#3fa7d6", 0.06, coat=0.8), YEL=G.mat("yel_t", "#ffb03b", 0.4), GLASS=G.mat("glass_t", "#2b3d4a", 0.1),
        TIRE=G.mat("tire", "#222222", 0.8), ORE=G.mat("ore_l", "#8a6a4a", 0.9, noise=30), PIN=G.mat("pin", "#12a89a", 0.3, coat=0.6),
        COPPER=G.mat("copper", "#c8733f", 0.25, metal=1.0), SOIL=G.mat("soil", "#8a6142", 0.9, noise=20),
        ROAD=G.mat("road", "#9aa0a6", 0.8),
    )

# ------------------------------------------------------------------ terrain / city
def build_terrain(p):
    mm = common_mats(); rnd = random.Random(p.get("seed", 3))
    mountains = p.get("mountains", True); river = p.get("river", True); city = float(p.get("city", 0)); future = p.get("future", False)
    def zf(x, y):
        z = 0.06 * fbm(x * 0.5, y * 0.5, 3)
        if mountains:
            m = max(0.0, (y - 0.6) / 3.0)
            ridge = 1 - abs(fbm(x * 0.55, y * 0.4, 4, 2))
            z += (m ** 1.3) * 2.3 * (0.55 + 0.6 * ridge)
        if river:
            ry = -1.6 + 0.35 * math.sin(x * 0.9)
            z -= 0.22 * math.exp(-((y - ry) / 0.32) ** 2)
        return z
    stops = [(0.0, "#c9b98f"), (0.06, "#8fc46a"), (0.22, "#6faa55"), (0.42, "#a88d6a"), (0.62, "#8c7b70")]
    if p.get("snow", True): stops += [(0.78, "#f7f2ea"), (1.0, "#ffffff")]
    else: stops += [(1.0, "#8c7b70")]
    gm = ramp_mat("terr", stops, -0.15, 2.6, 0.85, bump=0.15, bump_scale=6)
    polar_mesh("terrain", zf, 4.0, 70, 180, 0.7, (gm, mm["SOIL"]), sx=1.15)
    if river:
        G.cyl(0, 0, -0.16, -0.08, 3.9, mm["WATER"], seg=96).scale = (1.15, 1, 1)
    cx, cy = 0.4, -0.3
    if city > 0:
        n = int(10 + 90 * city); rad = 0.5 + 1.5 * city
        placed = []
        for k in range(n * 4):
            if len(placed) >= n: break
            a = rnd.uniform(0, math.tau); r = rad * math.sqrt(rnd.random())
            x, y = cx + r * math.cos(a) * 1.3, cy + r * math.sin(a) * 0.8
            if river and abs(y - (-1.6 + 0.35 * math.sin(x * 0.9))) < 0.38: continue
            if any((x - px) ** 2 + (y - py) ** 2 < 0.035 for px, py in placed): continue
            placed.append((x, y)); z = zf(x, y)
            h = rnd.uniform(0.08, 0.22) + (0.25 * rnd.random() if r < rad * 0.4 else 0)
            building(x, y, z - 0.02, 0.13, 0.11, h, mm["WALL"] if k % 3 else mm["WALL2"], mm["ROOF"] if k % 2 else mm["ROOF2"])
        if future:
            for k in range(7):
                a = k / 7 * math.tau; x, y = cx + 0.45 * math.cos(a), cy + 0.3 * math.sin(a)
                G.box(x - 0.07, y - 0.07, zf(x, y), x + 0.07, y + 0.07, zf(x, y) + 0.5 + 0.35 * (k % 3), mm["GLASSB"], 0.015)
            for k in range(10):
                x, y = cx - 1.9 + (k % 5) * 0.2, cy + 0.9 + (k // 5) * 0.22
                pn = G.box(x - 0.08, y - 0.06, zf(x, y) + 0.05, x + 0.08, y + 0.06, zf(x, y) + 0.065, mm["SOLAR"]); pn.rotation_euler = (math.radians(-25), 0, 0)
    nt = int(p.get("trees", 0))
    ox, oy = -1.5, -0.35; trees = []
    for k in range(nt * 30):
        if len(trees) >= nt: break
        a = rnd.uniform(0, math.tau); r = math.sqrt(rnd.random())
        x, y = ox + r * math.cos(a) * 1.5, oy + r * math.sin(a) * 0.75
        if river and abs(y - (-1.6 + 0.35 * math.sin(x * 0.9))) < 0.4: continue
        if any((x - tx) ** 2 + (y - ty) ** 2 < 0.07 for tx, ty in trees): continue
        trees.append((x, y)); apple_tree(x, y, zf(x, y) - 0.02, rnd.uniform(0.75, 1.0), mm, p.get("apples", True), rnd)
    if p.get("pin"):
        z = zf(cx, cy) + (0.55 if city > 0.5 else 0.25)
        G.sphere(cx, cy, z + 0.38, 0.15, mm["PIN"]); G.cyl(cx, cy, z, z + 0.36, 0.01, mm["PIN"], r2=0.11, seg=24)
        G.sphere(cx, cy, z + 0.38, 0.06, G.mat("pinw", "#ffffff", 0.3), sy=0.6)
    G.ANCH.update({"center": (0, 0, 0.2), "mountain": (0.0, 3.0, zf(0, 3.0)), "river": (-1.0, -1.6 + 0.35 * math.sin(-0.9), -0.1),
                   "city": (cx, cy, zf(cx, cy) + 0.2), "orchard": (ox, oy, zf(ox, oy) + 0.3),
                   "pin": (cx, cy, zf(cx, cy) + 0.9)})
    G.lights(1.1); G.setup(1080, 1080)
    look_cam((0, -9.2, 5.6), (0, 0.4, 0.2), 42)

# ------------------------------------------------------------------ quarry
def build_quarry(p):
    mm = common_mats(); L = int(p.get("levels", 8)); Rp, D = 2.8, 2.4
    def zr(r):
        if r >= Rp: return 0.0
        u = r / Rp * L; k = math.floor(u); f = u - k
        zk = -D * (1 - k / L)
        if f < 0.55: return zk
        t = (f - 0.55) / 0.45; t = t * t * (3 - 2 * t)
        return zk + (D / L) * t
    def zf(x, y):
        r = math.hypot(x / 1.25, y)
        return zr(r) + 0.025 * fbm(x * 2, y * 2, 2) + (0.08 * fbm(x * 0.4, y * 0.4, 2) if r > Rp else 0)
    gm = ramp_mat("pit", [(0.0, "#46525a"), (0.25, "#6b5f55"), (0.5, "#9c5530"), (0.75, "#b07f52"), (0.95, "#9c8a68"), (1.0, "#8fa168")],
                  -D, 0.05, 0.9, bump=0.5, bump_scale=14, slope_shade=0.55)
    polar_mesh("quarry", zf, 4.0, 110, 200, 0.7, (gm, mm["SOIL"]), sx=1.2)
    if p.get("water", True):
        w = G.cyl(0, 0, -D + 0.01, -D + 0.04, Rp / L * 0.66, mm["WATER"], seg=48); w.scale = (1.25, 1, 1)
    rnd = random.Random(5); trucks = []
    for k in range(int(p.get("trucks", 3))):
        lvl = L - 2 - (k % 3) * 2; r = (lvl + 0.25) / L * Rp; a = -1.2 + k * 1.05
        x, y = r * math.cos(a) * 1.25, r * math.sin(a)
        trucks.append((x, y, zf(x, y) + 0.1))
        truck(x, y, zf(x, y), 0.42, a + math.pi / 2, mm)
    b = (2.35 / L * Rp)
    G.ANCH.update({"center": (0, 0, -D * 0.5), "bottom": (0, 0, -D), "rim": (0, Rp, 0.0), "bench": (b * 1.25 * math.cos(-0.4), b * math.sin(-0.4), zr(b)),
                   "truck": trucks[0] if trucks else (0, 0, -D)})
    G.lights(1.15); G.setup(1080, 1080)
    look_cam((0, -8.6, 5.0), (0, 0.5, -1.0), 40)

# ------------------------------------------------------------------ ore
METALS = [("#c8733f", 1.0), ("#e8b830", 1.0), ("#d8dde2", 1.0), ("#8f98a3", 1.0), ("#9b4a4a", 0.6), ("#a9b6be", 1.0), ("#6b7177", 0.8),
          ("#b7a8c9", 0.8), ("#7aa0b8", 0.9), ("#c9c2a4", 0.9), ("#5d7f6e", 0.7), ("#d4a5a5", 0.8), ("#e0d070", 0.3)]

def build_ore(p):
    rnd = random.Random(7); split = float(p.get("split", 0)); n = int(p.get("metals", 13))
    rock = G.mat("rock", "#6f655c", 0.85, noise=18)
    vein = G.mat("vein", "#c8733f", 0.3, metal=0.9)
    gold = G.mat("vgold", "#e8b830", 0.25, metal=1.0)
    if split <= 0:
        ico(1.0, rock, 4, 0.45, 2, sc=(1.25, 1.0, 0.9))
        for k in range(18):
            a = rnd.uniform(0, math.tau); e = rnd.uniform(-0.6, 0.9); d = Vector((math.cos(a) * math.cos(e) * 1.2, math.sin(a) * math.cos(e) * 0.95, math.sin(e) * 0.85))
            if d.y > 0.4: continue
            G.sphere(*d, rnd.uniform(0.06, 0.13), vein if k % 4 else gold, sz=0.5)
    else:
        for k, (dx, dz) in enumerate([(-1, -0.3), (1, -0.25), (0.05, -0.75)]):
            ico(0.62, rock, 4, 0.5, k + 3, loc=(dx * (0.45 + 0.8 * split), 0.1, dz * (0.5 + 0.6 * split) - 0.2), sc=(1.1, 0.9, 0.8))
        for i in range(n):
            a = math.pi * (0.08 + 0.84 * i / max(1, n - 1))
            R = 1.5 + 0.5 * split; x, z = -math.cos(a) * R * 1.05, math.sin(a) * R * 0.9 - 0.1
            colr, met = METALS[i % len(METALS)]
            G.sphere(x, -0.2, z, 0.2, G.mat(f"m{i}", colr, 0.22, metal=met, coat=0.3))
            G.ANCH[f"m{i}"] = (x, -0.2, z)
    G.ANCH.update({"center": (0, 0, 0)})
    G.lights(1.1); G.setup(1080, 1080)
    look_cam((0, -6.3, 0.9), (0, 0, 0.15), 46)

# ------------------------------------------------------------------ flotation
def build_flotation(p):
    mm = common_mats(); rnd = random.Random(9)
    glass = G.mat("tank", "#dff4f6", 0.03, alpha=0.25, transmission=0.9)
    water = G.mat("fwater", "#6cb8c9", 0.05, alpha=0.4, transmission=0.8)
    metal = G.mat("steel", "#9aa6b0", 0.3, metal=1.0)
    G.cyl(0, 0, -1.4, 1.2, 1.05, glass, seg=64)
    G.cyl(0, 0, -1.38, 0.9, 1.0, water, seg=64)
    G.cyl(0, 0, -1.55, -1.4, 1.12, metal, seg=64); G.cyl(0, 0, 1.2, 1.26, 1.1, metal, seg=64)
    G.cyl(0, 0, -1.3, 1.4, 0.05, metal, seg=16)
    for k in range(4):
        b = G.box(-0.4, -0.04, -1.25, 0.4, 0.04, -1.1, metal, 0.01); b.rotation_euler = (0, 0, k * math.pi / 4)
    bub = G.mat("bub", "#eaf8ff", 0.05, alpha=0.85, transmission=0.3, coat=1.0)
    cu = G.mat("cup", "#d07a3a", 0.25, metal=1.0, emit=0.2)
    first = None
    for k in range(int(p.get("bubbles", 40))):
        r = rnd.uniform(0.06, 0.15); a = rnd.uniform(0, math.tau); rr = 0.85 * math.sqrt(rnd.random())
        x, y, z = rr * math.cos(a), rr * math.sin(a) * 0.5 - 0.3, rnd.uniform(-1.1, 0.75)
        G.sphere(x, y, z, r, bub)
        if first is None and y < -0.2: first = (x, y, z)
        if p.get("loaded", True):
            for j in range(5):
                u = rnd.uniform(0, math.tau); v = rnd.uniform(-1, 1)
                G.sphere(x + r * math.cos(u) * math.sqrt(1 - v * v), y + r * math.sin(u) * math.sqrt(1 - v * v), z + r * v, r * 0.22, cu)
    froth = G.mat("froth", "#8a7a5a", 0.5, noise=20)
    G.mb_mesh("froth", [((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), 0.95 + rnd.uniform(0, 0.12)), 0.22) for _ in range(40)], froth, 0.05)
    for k in range(25):
        a = rnd.uniform(0, math.tau); r = 0.85 * math.sqrt(rnd.random())
        G.sphere(r * math.cos(a), r * math.sin(a), 1.08 + rnd.uniform(0, 0.08), 0.03, cu)
    G.ANCH.update({"tank": (0, -1.0, 0), "froth": (0, -0.5, 1.05), "bubble": first or (0, -0.6, 0), "bottom": (0, -0.5, -1.2)})
    G.lights(1.15); G.setup(1080, 1200)
    look_cam((0, -6.2, 1.4), (0, 0, -0.05), 42)

# ------------------------------------------------------------------ globe
def lonlat(lon, lat, R=1.0):
    lo, la = math.radians(lon), math.radians(lat)
    return Vector((math.cos(lo) * math.cos(la), math.sin(lo) * math.cos(la), math.sin(la))) * R

def build_globe(p):
    R = 1.5
    m = bpy.data.materials.new("earth"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord"); tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(ROOT, "assets", "textures", "earth.jpg")); tx.extension = "REPEAT"
    nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); comb = nt.nodes.new("ShaderNodeCombineXYZ")
    def mnode(op, a=None, b=None, va=None, vb=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if a is not None: nt.links.new(a, n.inputs[0])
        else: n.inputs[0].default_value = va
        if b is not None: nt.links.new(b, n.inputs[1])
        elif vb is not None: n.inputs[1].default_value = vb
        return n.outputs[0]
    nt.links.new(tc.outputs["Object"], nrm.inputs[0]); nt.links.new(nrm.outputs["Vector"], sep.inputs[0])
    u = mnode("ADD", mnode("DIVIDE", mnode("ARCTAN2", sep.outputs["Y"], sep.outputs["X"]), vb=math.tau), vb=0.5)
    v = mnode("ADD", mnode("DIVIDE", mnode("ARCSINE", sep.outputs["Z"]), vb=math.pi), vb=0.5)
    nt.links.new(u, comb.inputs[0]); nt.links.new(v, comb.inputs[1])
    nt.links.new(comb.outputs[0], tx.inputs["Vector"]); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    g = G.sphere(0, 0, 0, R, m)
    for poly in g.data.polygons: poly.use_smooth = True
    # Olmaliq (69.6E, 40.85N) kameraga (-Y) qarasin
    olm = lonlat(69.6, 40.85)
    yaw = math.radians(-90) - math.atan2(olm.y, olm.x) + math.radians(p.get("spin", 0))
    rot = Matrix.Rotation(math.radians(40.85 - 14), 4, "X") @ Matrix.Rotation(yaw, 4, "Z")
    g.matrix_world = rot
    W = lambda v: (rot @ v.to_4d()).to_3d()
    pin_m = G.mat("gpin", "#ff4d5e", 0.3, emit=1.5)
    po = W(olm * R)
    G.sphere(*(po), 0.06, pin_m)
    arc_m = G.mat("arc", "#e0915f", 0.3, emit=2.0)
    targets = [(116, 40), (30, 50), (10, 50), (77, 25), (135, 35), (-0, 35)]
    for i in range(int(p.get("arcs", 0))):
        lo, la = targets[i % len(targets)]
        a, c = olm.normalized(), lonlat(lo, la).normalized()
        pts = []
        for k in range(41):
            t = k / 40; v = a.slerp(c, t) if hasattr(a, "slerp") else (a * (1 - t) + c * t).normalized()
            pts.append(tuple(W(v.normalized() * R * (1.0 + 0.35 * math.sin(t * math.pi)))))
        curve(pts, arc_m, 0.012, f"arc{i}")
        G.sphere(*W(c * R), 0.035, arc_m)
        G.ANCH[f"a{i}"] = tuple(W(c * R))
    G.ANCH.update({"center": (0, 0, 0), "olmaliq": tuple(po)})
    G.lights(1.2); G.setup(1080, 1080)
    look_cam((0, -6.4, 0.6), (0, 0, 0.05), 46)

# ------------------------------------------------------------------ shaft
def build_shaft(p):
    mm = common_mats(); cage = float(p.get("cage", 0.5))
    layers = [(0.0, -0.25, "#7aa35a"), (-0.25, -0.9, "#a07d5a"), (-0.9, -1.9, "#8a7464"), (-1.9, -3.0, "#6d625c")]
    for (z1, z0, h) in layers:
        G.box(-2.2, -0.5, z0, 2.2, 0.5, z1, G.mat("ly" + h, h, 0.9, noise=12))
    dark = G.mat("dark", "#1e2328", 0.9); light = G.mat("lamp", "#ffd27a", 0.3, emit=6.0)
    G.box(-0.95, -0.52, -2.75, -0.55, 0.3, 0.02, dark)
    G.box(-0.95, -0.52, -2.75, 1.9, 0.3, -2.25, dark)
    vein = G.mat("svein", "#c8733f", 0.3, metal=0.9, emit=0.15)
    for k in range(7):
        G.sphere(0.2 + k * 0.25, -0.5, -2.85 + 0.07 * math.sin(k * 1.7), 0.09, vein, sy=0.2)
    for k in range(5):
        G.sphere(-0.2 + k * 0.45, -0.52, -2.3, 0.04, light, sy=0.4)
    steel = G.mat("hf", "#b8673a", 0.4, metal=0.6)
    for sx in (-1, 1):
        G.box(-0.75 + sx * 0.25 - 0.03, -0.03, 0.02, -0.75 + sx * 0.25 + 0.03, 0.03, 1.2, steel)
    G.box(-1.05, -0.05, 1.15, -0.45, 0.05, 1.22, steel)
    G.cyl(-0.75, 0, 1.25, 1.3, 0.14, steel, seg=24)
    building(0.6, 0.0, 0.0, 0.9, 0.5, 0.45, mm["WALL"], mm["ROOF"])
    cz = -0.15 - cage * 2.2
    G.box(-0.9, -0.4, cz - 0.38, -0.6, 0.1, cz, mm["YEL"], 0.01)
    G.cyl(-0.75, -0.15, cz, 1.25, 0.008, G.mat("rope", "#333333", 0.5), seg=8)
    if p.get("miner", True):
        mx = 0.9
        G.cyl(mx, -0.35, -2.75, -2.48, 0.07, G.mat("suit", "#ff8a2a", 0.6), seg=16)
        G.sphere(mx, -0.35, -2.42, 0.06, G.mat("face", "#e7b98f", 0.5))
        G.sphere(mx, -0.35, -2.38, 0.07, mm["YEL"], sz=0.6); G.sphere(mx, -0.41, -2.38, 0.02, light)
    G.ANCH.update({"surface": (0, -0.5, 0.0), "headframe": (-0.75, -0.5, 1.2), "cage": (-0.75, -0.5, cz - 0.2), "tunnel": (0.6, -0.5, -2.5),
                   "miner": (0.9, -0.5, -2.55), "vein": (1.0, -0.5, -2.85)})
    G.lights(1.15); G.setup(1080, 1500)
    look_cam((1.2, -7.6, -0.4), (0.25, 0, -0.85), 42)

# ------------------------------------------------------------------ sprites
def build_osprite(p):
    mm = common_mats(); k = p["kind"]; cam = ((0, -3.3, 0.9), (0, 0, 0), 50); size = (500, 500)
    if k == "apple":
        G.sphere(0, 0, 0, 0.45, mm["APPLE"], sz=0.9); G.cyl(0, 0, 0.35, 0.6, 0.025, mm["TRUNK"])
        lf = G.sphere(0.16, 0, 0.55, 0.13, mm["LEAF"], sx=1.6, sy=0.4); lf.rotation_euler = (0, math.radians(-30), 0)
    elif k == "truck":
        truck(0, 0, -0.25, 1.0, math.radians(200), mm); cam = ((0, -3.0, 1.0), (0, 0, 0.05), 45); size = (600, 450)
    elif k == "cathode":
        G.box(-0.5, -0.04, -0.6, 0.5, 0.04, 0.5, mm["COPPER"], 0.02)
        G.box(-0.65, -0.05, 0.5, 0.65, 0.05, 0.6, G.mat("bar", "#9aa6b0", 0.3, metal=1.0), 0.02)
        cam = ((0.9, -3.0, 0.5), (0, 0, 0), 50); size = (500, 600)
    elif k == "wire":
        pts = [(0.45 * math.cos(t * 0.3), 0.45 * math.sin(t * 0.3), -0.45 + t * 0.012) for t in range(0, 76)]
        curve(pts, mm["COPPER"], 0.05, "coil"); cam = ((0, -3.0, 1.4), (0, 0, 0), 50)
    elif k in ("gold", "silver"):
        m = G.mat(k, "#e8b830" if k == "gold" else "#d8dde2", 0.2, metal=1.0)
        b = G.box(-0.5, -0.25, -0.15, 0.5, 0.25, 0.15, m, 0.06); b.scale = (1, 1, 1)
        G.box(-0.4, -0.18, 0.13, 0.4, 0.18, 0.2, m, 0.04)
        cam = ((0.8, -2.8, 1.4), (0, 0, 0), 50)
    elif k == "helmet":
        hy = G.mat("helm", "#ffa400", 0.35, coat=0.6)
        G.sphere(0, 0, 0, 0.5, hy, sz=0.8); G.cyl(0, 0, -0.08, -0.02, 0.64, hy, seg=48); G.box(-0.05, -0.5, -0.02, 0.05, 0.5, 0.42, hy, 0.03)
        G.sphere(0, -0.47, 0.12, 0.09, G.mat("hl", "#fff4c2", 0.2, emit=4.0), sy=0.5)
    elif k == "phone":
        G.box(-0.3, -0.04, -0.6, 0.3, 0.04, 0.6, G.mat("ph", "#1d2a33", 0.3), 0.06)
        G.box(-0.26, -0.05, -0.54, 0.26, -0.03, 0.54, G.mat("scr", "#12a89a", 0.2, emit=1.5))
        cam = ((0.6, -3.2, 0.3), (0.0, 0, 0.0), 45); size = (500, 650)
    elif k == "nugget":
        ico(0.4, G.mat("ng", "#c8733f", 0.3, metal=1.0), 3, 0.6, 4, sc=(1.2, 1, 0.8))
    G.lights(1.1); G.setup(*size)
    look_cam(*cam)

BUILDERS = {"terrain": build_terrain, "quarry": build_quarry, "ore": build_ore, "flotation": build_flotation,
            "globe": build_globe, "shaft": build_shaft, "osprite": build_osprite}
