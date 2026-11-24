"""@ai_olmaliq — HAQIQIY relyef va sun'iy yo'ldosh surati asosidagi 3D sahna (fotoreal).

Ma'lumot: assets/geo/olmaliq_dem.png (Copernicus DEM GLO-30) + olmaliq_s2.jpg (Sentinel-2 L2A, 2025-08-10).
Qamrov: 69.38–69.86 E, 40.72–41.00 N (~40×31 km). 1 Blender birligi = 1 km.

build "geo" params:
  target [lon, lat]     — kamera qaraydigan nuqta (yoki joy nomi: "olmaliq", "karyer", "qurama", "ohangaron", "dumba")
  dist (km=12)          — kameradan nishongacha masofa
  tilt (gradus=35)      — gorizontdan pastga qarash burchagi (90 = tepadan)
  heading (gradus=0)    — kamera qayerdan qaraydi: 0 = shimoldan janubga, 180 = janubdan shimolga
  lens (mm=35)  exag (1.6 — balandlik kuchaytirish)  sun (gradus balandlik=35)  sun_az (=135)
  pins [{"at": joy yoki [lon,lat], "name": "anker_nomi"}] — ankerlar (yozuv/halqa uchun) va qizil belgi (marker: true bo'lsa)
  fly {"frames": 12, "dist_to": 8, "heading_to": 20, "tilt_to": 45} — kamera harakati (videoda silliq uchish)
Ankerlar: center + pins nomlari + barcha joy nomlari.
"""
import os, math, json
import numpy as np
import bpy
from mathutils import Vector

G = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, "assets", "geo")
PLACES = {"olmaliq": (69.592, 40.862), "karyer": (69.648, 40.811), "qurama": (69.62, 40.745), "ohangaron": (69.56, 40.905),
          "dumba": (69.43, 40.78), "zavod": (69.555, 40.855)}

def register(mod):
    global G
    G = mod

def _meta():
    return json.load(open(os.path.join(GEO, "olmaliq_geo.json")))

def to_xy(lon, lat, m):
    W, S, E, N = m["bbox"]; kx, ky = m["km"]
    return (lon - W) / (E - W) * kx - kx / 2, (lat - S) / (N - S) * ky - ky / 2

def _place(v):
    return PLACES[v] if isinstance(v, str) else tuple(v)

def build_terrain_mesh(m, exag, step=1):
    from PIL import Image
    dem = np.asarray(Image.open(os.path.join(GEO, "olmaliq_dem.png")), dtype=np.float32)[::step, ::step]
    h, w = dem.shape; kx, ky = m["km"]
    z = (m["zmin"] + dem / 65535.0 * (m["zmax"] - m["zmin"])) / 1000.0 * exag
    z -= z.min()
    xs = np.linspace(-kx / 2, kx / 2, w, dtype=np.float32); ys = np.linspace(ky / 2, -ky / 2, h, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    verts = np.stack([X, Y, z], -1).reshape(-1, 3)
    idx = np.arange(h * w).reshape(h, w)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    quads = np.stack([a, d, c, b], -1).reshape(-1, 4)
    me = bpy.data.meshes.new("terrain")
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    nq = len(quads)
    me.loops.add(nq * 4); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
    me.polygons.add(nq); me.polygons.foreach_set("loop_start", np.arange(0, nq * 4, 4, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(nq, 4, dtype=np.int32))
    uv = me.uv_layers.new(name="uv")
    U = (X - X.min()) / (X.max() - X.min()); V = (Y - Y.min()) / (Y.max() - Y.min())
    uvs = np.stack([U, V], -1).reshape(-1, 2)[quads.ravel()]
    uv.data.foreach_set("uv", uvs.ravel().astype(np.float32))
    me.update(calc_edges=True); me.validate()
    me.polygons.foreach_set("use_smooth", np.ones(nq, dtype=bool))
    ob = bpy.data.objects.new("terrain", me); G.col().objects.link(ob)
    return ob, (xs, ys, z)

def height_at(grid, x, y):
    xs, ys, z = grid
    i = int(np.clip(np.searchsorted(-ys, -y), 0, len(ys) - 1)); j = int(np.clip(np.searchsorted(xs, x), 0, len(xs) - 1))
    return float(z[i, j])

def terrain_material():
    m = bpy.data.materials.new("sat"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.92
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(os.path.join(GEO, "olmaliq_s2.jpg")); tx.interpolation = "Cubic"
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "uv"; nt.links.new(uvn.outputs["UV"], tx.inputs["Vector"])
    # yorqinlik/kontrast (Sentinel TCI biroz xira)
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.inputs["Bright"].default_value = -0.04; bc.inputs["Contrast"].default_value = 0.25
    nt.links.new(tx.outputs["Color"], bc.inputs["Color"])
    # havo perspektivasi: uzoq joylar havorang tumanga botadi
    cam = nt.nodes.new("ShaderNodeCameraData")
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = -0.014
    nt.links.new(cam.outputs["View Distance"], k.inputs[0])
    ex = nt.nodes.new("ShaderNodeMath"); ex.operation = "EXPONENT"; nt.links.new(k.outputs[0], ex.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; nt.links.new(ex.outputs[0], inv.inputs[1])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(inv.outputs[0], mix.inputs["Factor"])
    nt.links.new(bc.outputs["Color"], mix.inputs[6]); mix.inputs[7].default_value = (0.42, 0.52, 0.66, 1)
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    return m

def sky_world(sun_elev, sun_az):
    w = bpy.data.worlds.new("sky"); G.scene().world = w; w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        try: sky.sky_type = t; break
        except Exception: continue
    for attr, val in (("sun_elevation", math.radians(sun_elev)), ("sun_rotation", math.radians(sun_az)), ("altitude", 1500.0),
                      ("air_density", 1.0), ("dust_density", 2.0), ("sun_disc", False)):
        try: setattr(sky, attr, val)
        except Exception: pass
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.18
    L = bpy.data.lights.new("sun", "SUN"); L.energy = 3.0; L.angle = math.radians(1.5); L.color = (1.0, 0.95, 0.88)
    o = bpy.data.objects.new("sun", L); G.col().objects.link(o)
    o.rotation_euler = (math.radians(90 - sun_elev), 0, math.radians(sun_az + 180))

def cam_pose(tx, ty, tz, dist, tilt, heading):
    t, hd = math.radians(tilt), math.radians(heading)
    # heading 0: kamera shimolda turib janubga qaraydi
    cx = tx + math.sin(hd) * dist * math.cos(t); cy = ty + math.cos(hd) * dist * math.cos(t); cz = tz + dist * math.sin(t)
    return (cx, cy, cz)

def build_geo(p):
    m = _meta(); exag = float(p.get("exag", 1.6))
    terr, grid = build_terrain_mesh(m, exag, int(p.get("step", 1)))
    terr.data.materials.append(terrain_material())
    sky_world(float(p.get("sun", 35)), float(p.get("sun_az", 135)))
    tlon, tlat = _place(p.get("target", "olmaliq"))
    tx, ty = to_xy(tlon, tlat, m); tz = height_at(grid, tx, ty)
    anchors = {"center": (tx, ty, tz)}
    for name, ll in PLACES.items():
        x, y = to_xy(*ll, m); anchors[name] = (x, y, height_at(grid, x, y))
    pinm = G.mat("pin", "#ff4d5e", 0.3, emit=3.0)
    for k, pin in enumerate(p.get("pins", [])):
        ll = _place(pin["at"]); x, y = to_xy(*ll, m); z = height_at(grid, x, y)
        anchors[pin.get("name", f"p{k}")] = (x, y, z + 0.05)
        if pin.get("marker"):
            s = float(p.get("dist", 12)) / 60
            G.cyl(x, y, z, z + s * 3, s * 0.12, pinm, seg=16); G.sphere(x, y, z + s * 3.4, s * 0.6, pinm)
    G.ANCH.update(anchors)
    dist, tilt, heading, lens = float(p.get("dist", 12)), float(p.get("tilt", 35)), float(p.get("heading", 0)), float(p.get("lens", 35))
    size = tuple(p.get("size", [1080, 1350]))
    G.setup(*size)
    sc = G.scene(); sc.render.film_transparent = False
    vs = sc.view_settings; vs.view_transform = "AgX"
    try: vs.look = "AgX - High Contrast"
    except Exception: pass
    vs.exposure = float(p.get("exposure", -0.9))
    sc.cycles.max_bounces = 3
    loc = cam_pose(tx, ty, tz, dist, tilt, heading)
    G.camera(loc, (tx, ty, tz), lens)
    cam = G.CAM["obj"]; cam.data.clip_end = 300; cam.data.clip_start = 0.05
    fly = p.get("fly")
    if fly:  # model3d.render_asset kadrlarni shu funksiya orqali oladi
        G.FLY.update({"n": int(fly.get("frames", 12)), "fn": lambda u: (
            cam_pose(tx, ty, tz, dist + (fly.get("dist_to", dist) - dist) * u, tilt + (fly.get("tilt_to", tilt) - tilt) * u,
                     heading + (fly.get("heading_to", heading) - heading) * u), (tx, ty, tz))})

BUILDERS = {"geo": build_geo}
