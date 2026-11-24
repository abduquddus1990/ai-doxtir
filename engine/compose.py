"""AI Doxtir — epizod JSON + render qilingan assetlar → 1080x1920 mp4 (musiqa bilan).

    python -m engine.compose episodes/e01_karies.json build/e01 out.mp4 [preview_times]
"""
import sys, os, math, json, glob, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "assets", "fonts", "Montserrat.ttf")
COL = {"teal": (18, 168, 154), "coral": (255, 77, 94), "amber": (255, 176, 59), "orange": (240, 120, 40),
       "ink": (29, 42, 51), "blue": (52, 132, 220), "purple": (140, 90, 210), "green": (60, 170, 90), "white": (255, 255, 255),
       "dentin": (176, 128, 40), "grey": (90, 105, 115), "copper": (184, 103, 58)}
def C(c): return COL[c] if isinstance(c, str) else tuple(c)

_fc = {}
def font(size, weight="ExtraBold"):
    k = (size, weight)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size)
        try: f.set_variation_by_name(weight)
        except Exception: pass
        _fc[k] = f
    return _fc[k]
def ease(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)
def eout(t): t = min(max(t, 0.0), 1.0); return 1 - (1 - t) ** 3
def eback(t):
    t = min(max(t, 0.0), 1.0); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ assets
class Asset:
    def __init__(self, path_png):
        meta_p = path_png.replace(".png", ".json")
        self.meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        sz = self.meta.get("size")
        if "frames" in self.meta:
            fs = sorted(glob.glob(path_png.replace(".png", "_[0-9][0-9][0-9].png")))
            self.frames = [self._load(f, sz) for f in fs]
            self.img = self.frames[len(self.frames) // 2]
            self._flows()
        else:
            self.frames = None
            self.img = self._load(path_png, sz)
        self.anchors = self.meta.get("anchors", {})

    @staticmethod
    def _load(p, sz):
        im = Image.open(p).convert("RGBA")
        if sz and im.size != tuple(sz): im = im.resize(tuple(sz), Image.BICUBIC)
        return im

    def _flows(self):
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        def g(im):
            a = np.array(im).astype(np.float32); al = a[:, :, 3:4] / 255
            return cv2.cvtColor((a[:, :, :3] * al + 255 * (1 - al)).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        self.np = [np.array(f).astype(np.float32) for f in self.frames]
        self.flows = []
        for i in range(len(self.frames) - 1):
            a, b = g(self.frames[i]), g(self.frames[i + 1])
            self.flows.append((dis.calc(a, b, None), dis.calc(b, a, None)))
        h, w = self.np[0].shape[:2]
        self.gy, self.gx = np.mgrid[0:h, 0:w].astype(np.float32)

    def at(self, u):
        """u in [0,1] across turntable"""
        if not self.frames: return self.img
        n = len(self.frames); x = min(max(u, 0), 0.9999) * (n - 1); i = int(x); f = x - i
        if f < 0.02 or i + 1 >= n: return self.frames[i]
        F01, F10 = self.flows[i]
        a = cv2.remap(self.np[i], self.gx + f * F10[..., 0], self.gy + f * F10[..., 1], cv2.INTER_LINEAR)
        b = cv2.remap(self.np[i + 1], self.gx + (1 - f) * F01[..., 0], self.gy + (1 - f) * F01[..., 1], cv2.INTER_LINEAR)
        return Image.fromarray(np.clip(a * (1 - f) + b * f, 0, 255).astype(np.uint8))

def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    img = np.array([233, 247, 246], np.float32) * (1 - t[..., None]) + np.array([255, 255, 255], np.float32) * t[..., None]
    for (cx, cy, r, a) in [(900, 300, 420, 0.10), (150, 1500, 520, 0.08), (700, 1150, 300, 0.05)]:
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        m = np.clip(1 - d, 0, 1) ** 1.5 * a
        img = img * (1 - m[..., None]) + np.array(COL["teal"], np.float32) * m[..., None]
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------------ drawing helpers
def paste_clip(canvas, im, x0, y0):
    cx0, cy0 = max(0, -x0), max(0, -y0)
    cx1, cy1 = min(im.width, W - x0), min(im.height, H - y0)
    if cx1 <= cx0 or cy1 <= cy0: return
    canvas.alpha_composite(im.crop((cx0, cy0, cx1, cy1)), (max(0, x0), max(0, y0)))

def sway(im, t, amp=2.2):
    """subtle 3D rotation (perspective) to keep stills alive"""
    if amp <= 0: return im
    w, h = im.size; a = math.radians(amp * math.sin(t * 0.9)); b = math.radians(amp * 0.6 * math.cos(t * 0.7))
    f = 2.2 * max(w, h)
    pts = []
    for (x, y) in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        z = x * math.sin(a) + y * math.sin(b); s = f / (f + z)
        pts.append((w / 2 + x * math.cos(a) * s, h / 2 + y * math.cos(b) * s))
    M = cv2.getPerspectiveTransform(np.float32([(0, 0), (w, 0), (w, h), (0, h)]), np.float32(pts))
    return Image.fromarray(cv2.warpPerspective(np.array(im), M, (w, h), flags=cv2.INTER_LINEAR))

def place(canvas, sprite, cx, cy, scale, rot=0.0, alpha=1.0, shadow=True):
    if scale <= 0.01 or alpha <= 0.01: return
    w, h = sprite.size
    s = sprite.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS if scale < 1 else Image.BICUBIC)
    if rot: s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = np.array(s); a[:, :, 3] = (a[:, :, 3] * alpha).astype(np.uint8); s = Image.fromarray(a)
    if shadow:
        sh = np.array(s); sh[:, :, :3] = (20, 60, 70); sh[:, :, 3] = (sh[:, :, 3] * 0.2).astype(np.uint8)
        sh = Image.fromarray(sh).filter(ImageFilter.GaussianBlur(16))
        paste_clip(canvas, sh, int(cx - s.width / 2), int(cy - s.height / 2 + 28))
    paste_clip(canvas, s, int(cx - s.width / 2), int(cy - s.height / 2))

def rich(canvas, y, text, size=72, alpha=1.0, acc="teal", base="ink", maxw=960):
    f = font(size); words = text.split(" "); lines, cur = [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if f.getlength(test.replace("*", "")) > maxw and cur: lines.append(cur); cur = w_
        else: cur = test
    lines.append(cur)
    d = ImageDraw.Draw(canvas); state = False
    for i, l in enumerate(lines):
        parts = l.split("*"); widths = [f.getlength(p) for p in parts]
        x = W / 2 - sum(widths) / 2; yy = y + i * size * 1.18 + (1 - alpha) * 24
        for j, p in enumerate(parts):
            if j > 0: state = not state
            c = C(acc) if state else C(base)
            d.text((x, yy), p, font=f, fill=(*c, int(255 * alpha)), anchor="lm"); x += widths[j]
    return y + len(lines) * size * 1.18

def lines_block(canvas, lines, lt, y0=340, step_delay=0.3):
    y = y0
    for i, ln in enumerate(lines):
        txt, size = ln[0], ln[1] if len(ln) > 1 else 72
        acc = ln[2] if len(ln) > 2 else "teal"
        delay = ln[3] if len(ln) > 3 else 0.15 + i * step_delay
        a = eout((lt - delay) / 0.4)
        if a <= 0:
            y += size * 1.2; continue
        y = rich(canvas, y, txt, size, a, acc) + 6

def badge(canvas, cx, cy, text, color, alpha=1.0, size=34):
    d = ImageDraw.Draw(canvas); f = font(size, "Bold"); w = f.getlength(text)
    s = eback(alpha) if alpha < 1 else 1.0
    pw, ph = (w / 2 + 34) * s, (size / 2 + 18) * s
    if pw <= 2: return
    d.rounded_rectangle([cx - pw, cy - ph, cx + pw, cy + ph], radius=int(ph), fill=(*C(color), int(255 * min(1, alpha * 1.5))))
    if s > 0.6: d.text((cx, cy + 1), text, font=f, fill=(255, 255, 255, int(255 * alpha)), anchor="mm")

def label(canvas, a_xy, t_xy, text, color, alpha, side="left"):
    if alpha <= 0: return
    d = ImageDraw.Draw(canvas); ax, ay = a_xy; tx, ty = t_xy; e = eout(alpha); col = C(color)
    mx, my = lerp(ax, tx, e), lerp(ay, ty, e)
    d.line([(ax, ay), (mx, my)], fill=(*col, int(255 * alpha)), width=4)
    d.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], fill=(255, 255, 255, int(255 * alpha)), outline=(*col, int(255 * alpha)), width=4)
    f = font(44); w = f.getlength(text)
    box = [tx - w - 36, ty - 34, tx, ty + 34] if side == "left" else [tx, ty - 34, tx + w + 36, ty + 34]
    d.rounded_rectangle(box, radius=34, fill=(255, 255, 255, int(235 * alpha)), outline=(*col, int(255 * alpha)), width=3)
    d.text(((box[0] + box[2]) / 2, ty + 1), text, font=f, fill=(*col, int(255 * alpha)), anchor="mm")

def glow(canvas, cx, cy, r, color, a):
    if a <= 0: return
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*C(color), int(200 * a)))
    canvas.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.45)))

def bolt(d, x, y, s, color, a):
    pts = [(0, -1), (0.45, -0.1), (0.1, -0.05), (0.35, 1), (-0.35, 0.05), (0.0, 0.0), (-0.25, -1)]
    d.polygon([(x + px * s, y + py * s) for (px, py) in pts], fill=(*C(color), int(255 * a)))

def sparkle(d, x, y, s, a, color="white"):
    if a <= 0: return
    pts = [(x + math.cos(i * math.pi / 4) * (s if i % 2 == 0 else s * 0.25), y + math.sin(i * math.pi / 4) * (s if i % 2 == 0 else s * 0.25)) for i in range(8)]
    d.polygon(pts, fill=(*C(color), int(255 * a)))

def arrow(d, p0, p1, color, a, w=12):
    if a <= 0: return
    x0, y0 = p0; x1, y1 = p1; x1, y1 = lerp(x0, x1, eout(a)), lerp(y0, y1, eout(a))
    d.line([(x0, y0), (x1, y1)], fill=(*C(color), int(255 * a)), width=w)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        d.line([(x1, y1), (x1 - 40 * math.cos(ang + s * 0.5), y1 - 40 * math.sin(ang + s * 0.5))], fill=(*C(color), int(255 * a)), width=w)

# ------------------------------------------------------------------ episode
def insert_sponsor(scenes, sponsor):
    """Split the stages scene in the middle and put a sponsor card between the halves."""
    if not sponsor or "mid" not in sponsor.get("placements", []): return scenes
    out = []; done = False
    for sc in scenes:
        if not done and sc["type"] == "stages" and len(sc["steps"]) >= 2:
            m = len(sc["steps"]) // 2
            a = dict(sc, steps=sc["steps"][:m]); b = dict(sc, steps=sc["steps"][m:], enter=False)
            out += [a, {"type": "sponsor", "dur": float(sponsor.get("mid_dur", 3.8))}, b]; done = True
        else:
            out.append(sc)
    if not done: out.insert(min(1, len(out)), {"type": "sponsor", "dur": float(sponsor.get("mid_dur", 3.8))})
    return out

def load_logo(path, size):
    if not path: return None
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(p): return None
    return Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)

class Episode:
    def __init__(self, ep_path, build_dir, cfg, sponsor=None):
        self.ep = json.load(open(ep_path, encoding="utf-8")); self.cfg = cfg; self.sp = sponsor
        self.A = {k: Asset(os.path.join(build_dir, k + ".png")) for k in self.ep["assets"]}
        self.BG = make_bg()
        self.logo = load_logo(cfg.get("logo"), 56)
        self.sp_logo = load_logo(sponsor.get("logo"), 240) if sponsor else None
        self.ep["scenes"] = insert_sponsor(self.ep["scenes"], sponsor)
        self.sp_start = None
        t = 0.0; self.timeline = []
        for sc in self.ep["scenes"]:
            if sc["type"] == "stages":
                d = sum(s["dur"] for s in sc["steps"])
            else:
                d = sc["dur"]
            if sc["type"] == "sponsor": self.sp_start = t
            self.timeline.append((t, t + d, sc)); t += d
        self.dur = t
        self.cuts = [a for (a, b, s) in self.timeline[1:]]

    # ---- stage view helpers
    def anchor(self, asset, name):
        a = self.A[asset].anchors
        if isinstance(name, list): return name
        return a.get(name, [self.A[asset].img.width / 2, self.A[asset].img.height / 2])

    def view_of(self, step):
        v = step.get("view", [1.2, "crown"])
        cx, cy = self.anchor(step["img"], v[1])
        return (v[0], cx, cy)

    def draw_view(self, canvas, img, view, t, yoff=0, shake=0.0, swamp=2.0, alpha=1.0):
        s, cx, cy = view
        if shake: cx += math.sin(t * 60) * shake; cy += math.cos(t * 47) * shake
        nw, nh = int(img.width * s), int(img.height * s)
        big = img.resize((nw, nh), Image.BICUBIC)
        big = sway(big, t, swamp)
        if alpha < 1:
            a = np.array(big); a[:, :, 3] = (a[:, :, 3] * alpha).astype(np.uint8); big = Image.fromarray(a)
        paste_clip(canvas, big, int(W / 2 - cx * s), int(1000 + yoff - cy * s))

    def scr(self, view, asset, key, yoff=0):
        s, cx, cy = view; px, py = self.anchor(asset, key)
        return W / 2 + (px - cx) * s, 1000 + yoff + (py - cy) * s

    # ---- scenes
    def sc_hook(self, c, sc, lt, dur):
        A = self.A[sc["img"]]
        im = A.at(lt / dur) if A.frames else A.img
        z0, z1 = sc.get("zoom", [0.95, 1.12])
        e = eout(lt / 0.6)
        sc_ = lerp(z0 * 0.8, z0, e) + (z1 - z0) * (lt / dur)
        pos = sc.get("pos", [540, 1150])
        if A.frames:
            place(c, im, pos[0], pos[1], sc_)
        else:
            v = (sc_, *self.anchor(sc["img"], sc.get("center", "crown")))
            self.draw_view(c, im, v, lt, yoff=pos[1] - 1000, swamp=2.5)
        if "series" in self.ep: badge(c, W / 2, 200, f'{self.ep["series"].upper()} #{self.ep["num"]}', "teal", eout(lt / 0.4), 30)
        lines_block(c, sc["lines"], lt, 300, 0.55)
        if sc.get("ring"):
            d = ImageDraw.Draw(c); a = ease((lt - 0.6) / 0.3); r = 70 + 12 * math.sin(lt * 8)
            x, y = sc["ring"]
            d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], outline=(*COL["coral"], int(220 * a)), width=7)

    def sc_cause(self, c, sc, lt, dur):
        A = self.A[sc["img"]]
        im = A.at(1.0) if A.frames else A.img
        pos = sc.get("pos", [540, 1330]); sc_ = sc.get("scale", 1.0)
        if A.frames: place(c, im, pos[0], pos[1], sc_)
        else: self.draw_view(c, im, (sc_, *self.anchor(sc["img"], sc.get("center", "crown"))), lt, yoff=pos[1] - 1000)
        badge(c, W / 2, 230, sc.get("badge", ["SABABI", "teal"])[0], sc.get("badge", ["SABABI", "teal"])[1], eout(lt / 0.4))
        lines_block(c, sc["lines"], lt, 340, 1.2)
        d = ImageDraw.Draw(c)
        for i, name in enumerate(sc.get("falling", [])):
            x = [300, 560, 790, 420, 680][i % 5]; delay = 0.2 + i * 0.25
            u = (lt - delay) / 0.9
            if u > 0:
                y = lerp(560, 860, eout(min(u, 1))); eaten = ease((lt - dur + 1.6 - i * 0.12) / 0.4) if sc.get("eat", True) else 0
                place(c, self.A[name].img, x, y, sc.get("fall_scale", 0.36) * (1 - eaten * 0.9), 30 * i + u * 40, alpha=1 - eaten)
        for i, name in enumerate(sc.get("crawlers", [])):
            x, y = [(210, 980), (870, 950), (420, 900), (690, 905)][i % 4]; delay = 0.9 + i * 0.2
            u = (lt - delay) / 0.5
            if u > 0:
                place(c, self.A[name].img, x, y + math.sin(lt * 7 + i) * 12 - (1 - eout(min(u, 1))) * 300, 0.52 * eback(min(u, 1)), math.sin(lt * 5 + i) * 8)
        if sc.get("drops") and lt > dur * 0.5:
            col = tuple(int(sc["drops"][i:i + 2], 16) for i in (1, 3, 5))
            for k in range(10):
                u = ((lt - dur * 0.5) * 1.3 + k * 0.37) % 1.0; x = 300 + (k * 97) % 480; y = lerp(930, 1060, u)
                d.ellipse([x - 12, y - 16, x + 12, y + 16], fill=(*col, int(220 * (1 - u))))

    def sc_stages(self, c, sc, lt, t_abs, first_in_episode):
        steps = sc["steps"]; tb = 0.0; idx = 0
        for i, s in enumerate(steps):
            if lt >= tb: idx = i; st_start = tb
            tb += s["dur"]
        st = steps[idx]; sl = lt - st_start
        prev = steps[idx - 1] if idx > 0 else None
        # camera
        v1 = self.view_of(st)
        if prev:
            v0 = self.view_of(prev); e = ease(sl / 0.8)
            view = tuple(lerp(a, b, e) for a, b in zip(v0, v1))
        else:
            view = v1
        # image (crossfade = growth)
        img = self.A[st["img"]].img
        if prev and prev["img"] != st["img"] and sl < 0.9:
            p_img = self.A[prev["img"]].img
            if p_img.size == img.size: img = Image.blend(p_img, img, ease(sl / 0.9))
            else:
                self.draw_view(c, p_img, view, t_abs, alpha=1 - ease(sl / 0.5))
        yoff = (1 - eout(lt / 0.7)) * 500 if (idx == 0 and lt < 0.7 and sc.get("enter", True)) else 0
        shake = 4.0 if any(f["kind"] == "shake" for f in st.get("fx", [])) and sl > 1.0 else 0.0
        self.draw_view(c, img, view, t_abs, yoff=yoff, shake=shake, alpha=min(1, lt / 0.3) if idx == 0 else 1)
        b = st.get("badge")
        if b: badge(c, W / 2, 230, b[0], b[1], eout(sl / 0.4))
        lines_block(c, st.get("lines", []), sl, 340, 0.3)
        d = ImageDraw.Draw(c)
        for f in st.get("fx", []):
            k = f["kind"]; dl = f.get("delay", 1.0); a = ease((sl - dl) / 0.35)
            if k == "shake" or a <= 0: continue
            if k == "label":
                label(c, self.scr(view, st["img"], f["at"], yoff), f["to"], f["text"], f.get("color", "teal"), a, f.get("side", "left"))
            elif k == "ring":
                x, y = self.scr(view, st["img"], f["at"], yoff); r = f.get("r", 95) + 8 * math.sin(sl * 6)
                d.ellipse([x - r, y - r, x + r, y + r], outline=(*C(f.get("color", "amber")), int(230 * a)), width=6)
            elif k == "bolts":
                x, y = self.scr(view, st["img"], f["at"], yoff); R = f.get("r", 190)
                for j, (dx, dy) in enumerate([(-1, -0.2), (0.95, -0.05), (-0.8, 0.65), (0.9, 0.75), (0, -1.2)][: f.get("n", 4)]):
                    aa = ease((sl - dl - j * 0.12) / 0.2) * (0.55 + 0.45 * abs(math.sin(sl * 9 + j)))
                    bolt(d, x + dx * R, y + dy * R * 0.8, f.get("size", 50), f.get("color", "orange"), aa)
            elif k == "glow":
                x, y = self.scr(view, st["img"], f["at"], yoff)
                glow(c, x, y + f.get("dy", 0), f.get("r", 170) * view[0] / 1.55, f.get("color", "coral"), a * (0.55 + 0.45 * abs(math.sin(sl * 5))))
                d = ImageDraw.Draw(c)
            elif k == "sparkle":
                x, y = self.scr(view, st["img"], f["at"], yoff)
                for j, (dx, dy, s) in enumerate([(-120, -90, 34), (130, -60, 26), (90, 110, 30), (-110, 90, 22)]):
                    aa = ease((sl - dl - j * 0.12) / 0.25) * (0.5 + 0.5 * math.sin(sl * 6 + j))
                    sparkle(d, x + dx, y + dy, s, aa, "teal" if j % 2 else "white")
            elif k == "arrow":
                p0 = self.scr(view, st["img"], f["from"], yoff); p1 = self.scr(view, st["img"], f["at"], yoff)
                arrow(d, p0, p1, f.get("color", "coral"), a)
            elif k == "sprite":
                x, y = self.scr(view, st["img"], f["at"], yoff); u = sl - dl
                if f.get("path") == "scrub":
                    x += math.sin(u * 14) * 150; y += 0
                elif f.get("path") == "circle":
                    x += math.cos(u * 6) * 60; y += math.sin(u * 6) * 40
                elif f.get("path") == "fall":
                    y -= (1 - eout(u / 0.6)) * 500
                place(c, self.A[f["name"]].img, x + f.get("dx", 0), y + f.get("dy", 0), f.get("scale", 0.6), f.get("rot", 0), alpha=a)
                d = ImageDraw.Draw(c)
            elif k == "drops":
                x, y = self.scr(view, st["img"], f["at"], yoff); col = C(f.get("color", [170, 230, 60]))
                for j in range(8):
                    u = ((sl - dl) * 1.2 + j * 0.37) % 1.0; xx = x - 200 + (j * 61) % 400; yy = y - 260 + u * 220
                    d.ellipse([xx - 11, yy - 15, xx + 11, yy + 15], fill=(*col, int(220 * (1 - u) * a)))
            elif k == "cross":
                x, y = self.scr(view, st["img"], f["at"], yoff); s = f.get("size", 70)
                d.line([(x - s, y - s), (x + s, y + s)], fill=(*COL["coral"], int(255 * a)), width=16)
                d.line([(x - s, y + s), (x + s, y - s)], fill=(*COL["coral"], int(255 * a)), width=16)
            elif k == "check":
                x, y = self.scr(view, st["img"], f["at"], yoff); s = f.get("size", 70)
                d.ellipse([x - s, y - s, x + s, y + s], fill=(*COL["teal"], int(235 * a)))
                d.line([(x - s * 0.45, y), (x - s * 0.1, y + s * 0.35), (x + s * 0.5, y - s * 0.35)], fill=(255, 255, 255, int(255 * a)), width=14)

    def sc_sponsor(self, c, sc, lt, dur):
        sp = self.sp; colr = sp.get("color", "#12A89A")
        if isinstance(colr, str) and colr.startswith("#"):
            h = colr.lstrip("#"); acc = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        else:
            acc = C(colr)
        d = ImageDraw.Draw(c); a = eout(lt / 0.45); s = eback(min(1, lt / 0.5))
        # card
        cw, ch = 900 * s, 1180 * s; x0, y0 = W / 2 - cw / 2, 1000 - ch / 2
        if cw > 20:
            sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 24, x0 + cw, y0 + ch + 24], 56, fill=(20, 60, 70, 60))
            c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
            d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 56, fill=(255, 255, 255, 255), outline=(*acc, 255), width=6)
        if lt < 0.35: return
        b = ease((lt - 0.35) / 0.4)
        d.rounded_rectangle([W / 2 - 90, 470, W / 2 + 90, 520], 25, fill=(*COL["grey"], int(230 * b)))
        d.text((W / 2, 496), "REKLAMA", font=font(26, "Bold"), fill=(255, 255, 255, int(255 * b)), anchor="mm")
        if self.sp_logo is not None:
            lg = self.sp_logo.copy(); al = np.array(lg); al[:, :, 3] = (al[:, :, 3] * b).astype(np.uint8)
            c.alpha_composite(Image.fromarray(al), (int(W / 2 - 120), 560))
        else:
            d.ellipse([W / 2 - 120, 560, W / 2 + 120, 800], fill=(*acc, int(255 * b)))
            ini = "".join(ch for w in sp["name"].split()[:2] for ch in w if ch.isalpha())[:1]
            ini = "".join(next((ch for ch in w if ch.isalpha()), "") for w in sp["name"].split()[:2]).upper() or ini
            d.text((W / 2, 682), ini, font=font(96), fill=(255, 255, 255, int(255 * b)), anchor="mm")
        y = 870
        rich(c, y, sp["name"], 70, b, "teal"); y += 96
        if sp.get("tagline"): rich(c, y, sp["tagline"], 42, ease((lt - 0.6) / 0.4)); y += 80
        if sp.get("mid_text"):
            mt = ease((lt - 0.9) / 0.4); y = rich(c, y, sp["mid_text"], 50, mt, base=acc if isinstance(acc, tuple) else "teal") + 20
        rows = [r for r in (sp.get("phone"), sp.get("address"), sp.get("telegram") or sp.get("instagram")) if r]
        for i, r in enumerate(rows):
            ra = ease((lt - 1.2 - i * 0.2) / 0.35)
            d.ellipse([200, y + i * 78 - 14, 228, y + i * 78 + 14], fill=(*acc, int(255 * ra)))
            d.text((250, y + i * 78), r, font=font(42, "SemiBold"), fill=(*COL["ink"], int(255 * ra)), anchor="lm")

    def sponsor_badge(self, c, t):
        sp = self.sp
        if not sp or "corner" not in sp.get("placements", []): return
        start = (self.sp_start + self.timeline[0][1] * 0) if self.sp_start is not None else 0.0
        if self.sp_start is not None: start = self.sp_start + float(sp.get("mid_dur", 3.8))
        if t < start + 0.3: return
        for (a, b, sc) in self.timeline:
            if a <= t < b and sc["type"] in ("cta", "sponsor"): return
        al = ease((t - start - 0.3) / 0.5)
        d = ImageDraw.Draw(c); f = font(30, "Bold"); txt = f"Hamkor: {sp['name']}"; w = f.getlength(txt)
        d.rounded_rectangle([W / 2 - w / 2 - 34, 1818, W / 2 + w / 2 + 34, 1878], 30, fill=(255, 255, 255, int(225 * al)), outline=(*COL["teal"], int(200 * al)), width=3)
        d.text((W / 2, 1849), txt, font=f, fill=(*COL["ink"], int(255 * al)), anchor="mm")

    def sc_cta(self, c, sc, lt, dur):
        A = self.A[sc["img"]]; im = A.at(0.5) if A.frames else A.img
        pos = sc.get("pos", [540, 900])
        if A.frames: place(c, im, pos[0], pos[1], sc.get("scale", 0.95) + 0.03 * lt, alpha=ease(lt / 0.4))
        else: self.draw_view(c, im, (sc.get("scale", 1.0) * (1 + 0.02 * lt), *self.anchor(sc["img"], sc.get("center", "crown"))), lt, yoff=pos[1] - 1000, alpha=ease(lt / 0.4))
        d = ImageDraw.Draw(c)
        for k, (dx, dy, s) in enumerate([(-260, -260, 40), (240, -200, 30), (280, 120, 34), (-280, 140, 26)]):
            sparkle(d, W / 2 + dx, pos[1] + dy, s, ease((lt - 0.4 - k * 0.1) / 0.3) * (0.6 + 0.4 * math.sin(lt * 5 + k)), "teal")
        badge(c, W / 2, 230, sc.get("badge", ["MASLAHAT", "teal"])[0], "teal", eout(lt / 0.4))
        lines_block(c, sc["lines"], lt, 340, 0.2)
        a = ease((lt - 1.0) / 0.5); cfg = self.cfg
        title, sub = cfg["cta_title"], cfg["cta_sub"]
        sp = self.sp
        if sp and "end" in sp.get("placements", []):
            title = sp["name"]; sub = " · ".join(x for x in (sp.get("phone"), sp.get("address")) if x)
            d.text((W / 2, 1395), "REKLAMA", font=font(24, "Bold"), fill=(*COL["grey"], int(220 * a)), anchor="mm")
        d.rounded_rectangle([110, 1420, W - 110, 1640], radius=44, fill=(255, 255, 255, int(230 * a)), outline=(*COL["teal"], int(255 * a)), width=4)
        f1 = font(46); 
        while f1.size > 30 and f1.getlength(title) > W - 300: f1 = font(f1.size - 2)
        d.text((W / 2, 1500), title, font=f1, fill=(*COL["teal"], int(255 * a)), anchor="mm")
        f2 = font(34, "SemiBold")
        while f2.size > 22 and f2.getlength(sub) > W - 300: f2 = font(f2.size - 2, "SemiBold")
        d.text((W / 2, 1568), sub, font=f2, fill=(*COL["ink"], int(205 * a)), anchor="mm")
        if cfg.get("cta_footer"): d.text((W / 2, 1700), cfg["cta_footer"], font=font(36, "Bold"), fill=(*COL["ink"], int(220 * a)), anchor="mm")
        disc = self.ep.get("disclaimer", cfg.get("disclaimer", ""))
        if disc: d.text((W / 2, 1830), disc, font=font(26, "SemiBold"), fill=(*COL["grey"], int(255 * a)), anchor="mm")

    def frame(self, t):
        c = self.BG.copy()
        for i, (a, b, sc) in enumerate(self.timeline):
            if a <= t < b or (i == len(self.timeline) - 1 and t >= a):
                lt = t - a; dur = b - a
                {"hook": lambda: self.sc_hook(c, sc, lt, dur), "cause": lambda: self.sc_cause(c, sc, lt, dur),
                 "stages": lambda: self.sc_stages(c, sc, lt, t, i == 0), "cta": lambda: self.sc_cta(c, sc, lt, dur),
                 "sponsor": lambda: self.sc_sponsor(c, sc, lt, dur)}[sc["type"]]()
                break
        self.sponsor_badge(c, t)
        d = ImageDraw.Draw(c)
        hf = font(30, "Bold"); hw = hf.getlength(self.cfg["handle"])
        if self.logo is not None:
            gx = W / 2 - (hw + 66) / 2
            c.alpha_composite(self.logo, (int(gx), 72)); d = ImageDraw.Draw(c)
            d.text((gx + 66, 100), self.cfg["handle"], font=hf, fill=(*COL["ink"], 170), anchor="lm")
        else:
            d.text((W / 2, 100), self.cfg["handle"], font=hf, fill=(*COL["ink"], 150), anchor="mm")
        if self.cfg.get("stamp"):
            sf = font(20, "Bold"); sw = sf.getlength(self.cfg["stamp"])
            d.rounded_rectangle([W - 40 - sw - 36, 82, W - 40, 118], 18, fill=(18, 52, 59, 200))
            d.text((W - 40 - sw / 2 - 18, 100), self.cfg["stamp"], font=sf, fill=(247, 242, 234, 235), anchor="mm")
        out = np.array(c.convert("RGB"))
        if t < 0.25: out = (out * ease(t / 0.25)).astype(np.uint8)
        if t > self.dur - 0.6:
            k = ease((t - self.dur + 0.6) / 0.6); out = (out * (1 - k) + 255 * k).astype(np.uint8)
        for tb in self.cuts:
            if tb <= t < tb + 0.18:
                k = 1 - (t - tb) / 0.18; out = (out * (1 - 0.55 * k) + 255 * 0.55 * k).astype(np.uint8)
        return out

# ------------------------------------------------------------------ music
def make_music(path, dur, cuts, seed=0):
    from scipy.signal import lfilter, butter
    rng = np.random.RandomState(seed)
    sr = 44100; n = int(sr * dur); t = np.arange(n) / sr; out = np.zeros(n)
    bpm = [108, 112, 104, 116][seed % 4]; beat = 60 / bpm; bar = beat * 4
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    progs = [[[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]],
             [[62, 65, 69, 72], [58, 62, 65, 69], [60, 64, 67, 71], [57, 60, 64, 67]],
             [[57, 60, 64, 67], [53, 57, 60, 64], [60, 64, 67, 71], [55, 59, 62, 67]]]
    chords = progs[seed % 3]
    for i in range(int(dur / bar) + 1):
        ch = chords[i % 4]; s0 = int(i * bar * sr); s1 = min(n, int((i + 1) * bar * sr))
        if s0 >= n: break
        tt = t[s0:s1] - i * bar; env = np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
        for m in ch: out[s0:s1] += env * np.sin(2 * np.pi * note(m) * tt) * 0.045
        out[s0:s1] += env * np.sin(2 * np.pi * note(ch[0] - 24) * tt) * 0.2
    step = beat / 2; pat = [[0, 2, 3, 1, 2, 3, 1, 2], [0, 1, 2, 3, 2, 1, 2, 3], [3, 2, 1, 0, 1, 2, 3, 2]][seed % 3]
    for k in range(int(dur / step)):
        ch = chords[int(k * step / bar) % 4]; m = ch[pat[k % 8]] + 12
        s0 = int(k * step * sr); L = int(0.35 * sr)
        if s0 + L > n: break
        tt = np.arange(L) / sr
        out[s0:s0 + L] += np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 12) * 0.12
    for k in range(int(dur / beat)):
        s0 = int(k * beat * sr); L = int(0.25 * sr)
        if s0 + L > n or k * beat > dur - 2: continue
        tt = np.arange(L) / sr
        out[s0:s0 + L] += np.sin(2 * np.pi * (55 + 80 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * 0.35
        h0 = s0 + int(beat / 2 * sr); HL = int(0.04 * sr)
        if h0 + HL < n: out[h0:h0 + HL] += rng.randn(HL) * np.exp(-np.arange(HL) / sr * 100) * 0.03
    b, a = butter(2, 0.07)
    for tb in cuts:
        L = int(0.6 * sr); s0 = int((tb - 0.35) * sr)
        if s0 < 0 or s0 + L > n: continue
        out[s0:s0 + L] += lfilter(b, a, rng.randn(L)) * np.sin(np.linspace(0, np.pi, L)) ** 2 * 0.45
    out *= np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 1.2)
    out = out / np.max(np.abs(out)) * 0.85
    st = np.stack([out, out], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st * 32767).astype(np.int16).tobytes())

def render_video(ep_path, build_dir, out_mp4, cfg, preview_times=None, sponsor=None):
    E = Episode(ep_path, build_dir, cfg, sponsor)
    if preview_times:
        outs = []
        for tt in preview_times:
            p = os.path.join(build_dir, f"pv_{tt:05.2f}.jpg"); Image.fromarray(E.frame(tt)).save(p, quality=86); outs.append(p)
        return outs, E.dur
    music = os.path.join(build_dir, "music.wav"); make_music(music, E.dur, E.cuts, E.ep.get("num", 0))
    tmp = os.path.join(build_dir, "video.tmp.mp4"); nfr = int(E.dur * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(nfr):
        p.stdin.write(E.frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError("ffmpeg (video) xato")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", music, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    os.remove(tmp)
    return out_mp4, E.dur

if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
    pv = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    print(render_video(sys.argv[1], sys.argv[2], sys.argv[3], cfg, pv))
