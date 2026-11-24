"""AI Doxtir — navbatdagi epizodni 3D render qiladi, montaj qiladi va @ai_doxtirBot orqali
video + tavsif matnini (Instagram uchun) yuboradi.

  python run.py                                  # navbatdagi epizod, to'liq sifat, Telegramga yuborish
  python run.py --episode e03_implant            # aniq epizod
  python run.py --quality preview --no-send      # tez sinov (past sifat)
  python run.py --episode e01_karies --preview-times 2,10,20   # bir nechta kadr (jpg)
  python run.py --sponsor namuna_klinika         # hamkorni majburan qo'shish (sinov uchun)
  python run.py --no-sponsor                     # reklamasiz
  python run.py --check                          # GitHub Actions: bugun yuborilganmi?
  python run.py --list                           # navbat holati
"""
import os, sys, json, glob, hashlib, argparse, shutil, subprocess, datetime as dt, time
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
try:
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
except Exception:
    pass
from engine.compose import render_video
from publishers import telegram

EP_DIR = os.path.join(ROOT, "episodes"); BUILD = os.path.join(ROOT, "build"); OUT = os.path.join(ROOT, "out")
SENT = os.path.join(ROOT, "data", "sent.json")

def today():
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5)).date()

def load_sent():
    d = json.load(open(SENT, encoding="utf-8")) if os.path.exists(SENT) else {}
    d.setdefault("sent", []); d.setdefault("log", {}); d.setdefault("sponsor_counts", {})
    return d

def save_sent(d):
    os.makedirs(os.path.dirname(SENT), exist_ok=True)
    d["log"] = {k: d["log"][k] for k in sorted(d["log"])[-30:]}
    json.dump(d, open(SENT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def episodes():
    return sorted(glob.glob(os.path.join(EP_DIR, "*.json")))

def next_episode(d):
    for p in episodes():
        if os.path.basename(p)[:-5] not in d["sent"]: return p
    return None

# ------------------------------------------------------------------ sponsors
def load_sponsors():
    p = os.path.join(ROOT, "sponsors.json")
    return json.load(open(p, encoding="utf-8")).get("sponsors", []) if os.path.exists(p) else []

def pick_sponsor(ep, d, force_id=None):
    sps = load_sponsors()
    if force_id:
        for s in sps:
            if s["id"] == force_id: return s
        raise SystemExit(f"Hamkor topilmadi: {force_id}")
    t = today().isoformat(); tags = set(ep.get("tags", []))
    for s in sps:
        if not s.get("active"): continue
        if s.get("from") and t < s["from"]: continue
        if s.get("to") and t > s["to"]: continue
        if s.get("tags") and not (tags & set(s["tags"])): continue
        if s.get("max_videos") and d["sponsor_counts"].get(s["id"], 0) >= s["max_videos"]: continue
        return s
    return None

def build_caption(ep, cfg, sponsor):
    txt = ep["instagram"].rstrip()
    if sponsor and "caption" in sponsor.get("placements", []):
        lines = [f"🤝 Hamkor: {sponsor['name']}" + (f" — {sponsor['tagline']}" if sponsor.get("tagline") else "")]
        contact = " · ".join(x for x in (sponsor.get("phone") and "📞 " + sponsor["phone"], sponsor.get("address") and "📍 " + sponsor["address"],
                                          sponsor.get("instagram") or sponsor.get("telegram")) if x)
        if contact: lines.append(contact)
        lines.append("#reklama")
        txt += "\n\n" + "\n".join(lines)
    if cfg.get("caption_footer"): txt += "\n\n" + cfg["caption_footer"]
    return txt

# ------------------------------------------------------------------ 3D assets
def render_assets(ep, bdir, quality):
    os.makedirs(bdir, exist_ok=True)
    cache = os.path.join(BUILD, "_cache"); os.makedirs(cache, exist_ok=True)
    engine_sig = hashlib.sha1(open(os.path.join(ROOT, "engine", "model3d.py"), "rb").read()).hexdigest()[:10]
    for name, spec in ep["assets"].items():
        key = hashlib.sha1((json.dumps(spec, sort_keys=True) + quality + engine_sig).encode()).hexdigest()[:16]
        cpng = os.path.join(cache, key + ".png")
        if not os.path.exists(cpng.replace(".png", ".json")):
            t0 = time.time()
            r = subprocess.run([sys.executable, "-m", "engine.model3d", json.dumps(spec), cpng, quality], cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0 or "ASSET_OK" not in r.stdout:
                print(r.stdout[-2000:], r.stderr[-2000:]); raise RuntimeError(f"3D render xato: {name}")
            print(f"  asset {name}: {time.time() - t0:.0f}s", flush=True)
        for f in glob.glob(cpng.replace(".png", "*")):
            shutil.copy(f, os.path.join(bdir, name + os.path.basename(f)[len(key):]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode"); ap.add_argument("--quality", default="full", choices=["full", "preview"])
    ap.add_argument("--no-send", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true"); ap.add_argument("--preview-times")
    ap.add_argument("--sponsor"); ap.add_argument("--no-sponsor", action="store_true")
    ap.add_argument("--mark-sent", action="store_true", help="--episode bilan: yuborilgan deb belgilash")
    a = ap.parse_args()
    d = load_sent()
    if a.check:
        print("skip=" + ("true" if d["log"].get(today().isoformat()) else "false")); return
    if a.list:
        for p in episodes():
            eid = os.path.basename(p)[:-5]; print(("✅ " if eid in d["sent"] else "⏳ ") + eid)
        return
    cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
    path = os.path.join(EP_DIR, a.episode + ".json") if a.episode else next_episode(d)
    if not path:
        telegram.notify("AI Doxtir: navbatdagi barcha epizodlar yuborilgan. Yangi epizod qo'shing (episodes/).")
        print("Navbat bo'sh"); return
    ep = json.load(open(path, encoding="utf-8")); eid = ep["id"]
    sponsor = None if a.no_sponsor else pick_sponsor(ep, d, a.sponsor)
    print(f"Epizod: {eid} — {ep['title']} ({a.quality})" + (f" · hamkor: {sponsor['name']}" if sponsor else ""), flush=True)
    bdir = os.path.join(BUILD, eid + ("_pv" if a.quality == "preview" else ""))
    render_assets(ep, bdir, a.quality)
    os.makedirs(OUT, exist_ok=True)
    caption = build_caption(ep, cfg, sponsor)
    if a.preview_times:
        outs, dur = render_video(path, bdir, None, cfg, [float(x) for x in a.preview_times.split(",")], sponsor)
        print("preview:", outs, "dur", dur); return
    mp4 = os.path.join(OUT, f"{eid}.mp4")
    _, dur = render_video(path, bdir, mp4, cfg, None, sponsor)
    open(os.path.join(OUT, f"{eid}.txt"), "w", encoding="utf-8").write(caption)
    print(f"Video: {mp4} ({dur:.1f} s)\nTavsif: out/{eid}.txt", flush=True)
    if a.no_send: return
    chats = [c.strip() for c in os.environ.get("TG_MANUAL_CHAT_IDS", "").split(",") if c.strip()]
    telegram.send_manual(mp4, ep, caption, chats)
    if not a.episode or a.mark_sent:
        d["sent"] = sorted(set(d["sent"]) | {eid})
        d["log"].setdefault(today().isoformat(), []).append(eid)
    if sponsor:
        d["sponsor_counts"][sponsor["id"]] = d["sponsor_counts"].get(sponsor["id"], 0) + 1
    save_sent(d)
    left = sum(1 for p in episodes() if os.path.basename(p)[:-5] not in d["sent"])
    telegram.notify(f"AI Doxtir: {eid} yuborildi. Navbatda qoldi: {left}")

if __name__ == "__main__":
    main()
