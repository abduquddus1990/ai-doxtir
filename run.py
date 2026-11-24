"""AI Doxtir / AI Olmaliq — navbatdagi epizodni 3D render qiladi, montaj qiladi va bot orqali
video + tavsif matnini (Instagram uchun) yuboradi. Navbat tugasa, yangi ssenariylarni avtomatik yozadi.

  python run.py                                   # doxtir: navbatdagi epizod, yuborish
  python run.py --channels doxtir,olmaliq --slot auto --send-at auto   # jadval (GitHub Actions)
  python run.py --channel olmaliq --episode o01_nomi                 # aniq epizod (navbatni o'zgartirmaydi)
  python run.py --quality preview --no-send       # tez sinov (past sifat)
  python run.py --episode e01_karies --preview-times 2,10,20         # bir nechta kadr (jpg)
  python run.py --sponsor namuna_klinika          # hamkorni majburan qo'shish (sinov uchun)
  python run.py --check --channels doxtir,olmaliq --slot auto        # GitHub Actions: bu slot yuborilganmi?
  python run.py --list --channel olmaliq          # navbat holati
  python run.py --autogen --channel doxtir        # ssenariylarni hozir yozish (sinov)
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
from publishers import telegram

BUILD = os.path.join(ROOT, "build"); OUT = os.path.join(ROOT, "out")
CHANNELS = {
    "doxtir":  {"cfg": "config.json", "episodes": "episodes", "sent": "data/sent.json", "prefix": "e"},
    "olmaliq": {"cfg": "channels/olmaliq/config.json", "episodes": "channels/olmaliq/episodes", "sent": "data/sent_olmaliq.json", "prefix": "o"},
}
SLOTS = {"am": "06:00", "pm": "19:00"}   # Toshkent vaqti

def now_tk(): return dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5)
def today(): return now_tk().date()
def auto_slot(): return "am" if now_tk().hour < 12 else "pm"

class Channel:
    def __init__(self, name):
        c = CHANNELS[name]; self.name = name; self.prefix = c["prefix"]
        self.cfg_path = os.path.join(ROOT, c["cfg"]); self.ep_dir = os.path.join(ROOT, c["episodes"]); self.sent_path = os.path.join(ROOT, c["sent"])
        self.cfg = json.load(open(self.cfg_path, encoding="utf-8"))
        self.d = self.load_sent()

    def load_sent(self):
        d = json.load(open(self.sent_path, encoding="utf-8")) if os.path.exists(self.sent_path) else {}
        for k, v in (("sent", []), ("log", {}), ("sponsor_counts", {}), ("failed", [])): d.setdefault(k, v)
        return d

    def save(self):
        os.makedirs(os.path.dirname(self.sent_path), exist_ok=True)
        d = self.d; d["log"] = {k: d["log"][k] for k in sorted(d["log"])[-60:]}
        json.dump(d, open(self.sent_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def episodes(self): return sorted(glob.glob(os.path.join(self.ep_dir, "*.json")))
    def done(self, p):
        eid = os.path.basename(p)[:-5]; return eid in self.d["sent"] or eid in self.d["failed"]
    def queue(self): return [p for p in self.episodes() if not self.done(p)]
    def slot_done(self, slot): return f"{today().isoformat()}_{slot}" in self.d["log"]

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
    sig = b"".join(open(os.path.join(ROOT, "engine", f), "rb").read() for f in ("model3d.py", "olmaliq3d.py"))
    engine_sig = hashlib.sha1(sig).hexdigest()[:10]
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

def make_video(ch, path, quality="full", sponsor_id=None, no_sponsor=False, preview_times=None):
    from engine.compose import render_video
    ep = json.load(open(path, encoding="utf-8")); eid = ep["id"]
    sponsor = None if no_sponsor else pick_sponsor(ep, ch.d, sponsor_id)
    print(f"[{ch.name}] Epizod: {eid} — {ep['title']} ({quality})" + (f" · hamkor: {sponsor['name']}" if sponsor else ""), flush=True)
    bdir = os.path.join(BUILD, eid + ("_pv" if quality == "preview" else ""))
    render_assets(ep, bdir, quality)
    if preview_times:
        outs, dur = render_video(path, bdir, None, ch.cfg, preview_times, sponsor)
        print("preview:", outs, "dur", dur); return None
    os.makedirs(OUT, exist_ok=True)
    caption = build_caption(ep, ch.cfg, sponsor)
    mp4 = os.path.join(OUT, f"{eid}.mp4")
    _, dur = render_video(path, bdir, mp4, ch.cfg, None, sponsor)
    open(os.path.join(OUT, f"{eid}.txt"), "w", encoding="utf-8").write(caption)
    print(f"[{ch.name}] Video: {mp4} ({dur:.1f} s)", flush=True)
    return {"ch": ch, "ep": ep, "mp4": mp4, "caption": caption, "sponsor": sponsor}

def wait_until(hhmm, max_wait=40 * 60):
    h, m = map(int, hhmm.split(":")); n = now_tk()
    target = n.replace(hour=h, minute=m, second=0, microsecond=0)
    wait = (target - n).total_seconds()
    if 0 < wait <= max_wait:
        print(f"Yuborish vaqtigacha kutish: {wait / 60:.1f} daqiqa ({hhmm} Toshkent)", flush=True); time.sleep(wait)

def chats():
    return [c.strip() for c in os.environ.get("TG_MANUAL_CHAT_IDS", "").split(",") if c.strip()]

def run_autogen(ch):
    """Navbat tugadi: API kaliti bo'lsa — avtomatik yozadi, bo'lmasa — qo'lda yuklashni eslatadi."""
    from tools import autogen
    if not os.environ.get("ANTHROPIC_API_KEY"):
        telegram.notify(f"AI {ch.name}: navbatdagi ssenariylar tugadi. Yangi JSON faylni GitHub'da inbox/{ch.name}/ papkasiga yuklang "
                        f"(yo'riqnoma: docs/SSENARIY_YOZISH.md).")
        return []
    new = autogen.generate(ch)
    if new:
        telegram.send_text(autogen.review_text(ch, new), chats())
        telegram.notify(f"AI {ch.name}: {len(new)} ta yangi ssenariy yozildi va navbatga qo'shildi.")
    return new

def run_inbox(ch):
    from tools import inbox, autogen
    added, errors = inbox.process(ch)
    if added:
        telegram.send_text(autogen.review_text(ch, added), chats())
    if errors:
        telegram.send_text(f"⚠️ {ch.cfg.get('bot_head', ch.name)}: inbox'dagi {len(errors)} ta ssenariy qabul qilinmadi:\n\n" + "\n\n".join(errors), chats())
    if added or errors: print(f"[{ch.name}] inbox: +{len(added)}, xato {len(errors)}")

def check_episode(ch, ep):
    from tools.autogen import validate, SPECS
    return validate(ep, SPECS[ch.name])

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", default="doxtir", choices=list(CHANNELS)); ap.add_argument("--channels")
    ap.add_argument("--episode"); ap.add_argument("--quality", default="full", choices=["full", "preview"])
    ap.add_argument("--no-send", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--slot", help="am | pm | auto — jadval sloti (bitta slotga bitta video)")
    ap.add_argument("--send-at", help="HH:MM yoki auto — render tugagach shu Toshkent vaqtigacha kutib yuborish")
    ap.add_argument("--list", action="store_true"); ap.add_argument("--preview-times")
    ap.add_argument("--sponsor"); ap.add_argument("--no-sponsor", action="store_true")
    ap.add_argument("--mark-sent", action="store_true", help="--episode bilan: yuborilgan deb belgilash")
    ap.add_argument("--autogen", action="store_true", help="yangi ssenariylarni hozir yozish")
    a = ap.parse_args()
    names = [x.strip() for x in a.channels.split(",")] if a.channels else [a.channel]
    slot = auto_slot() if a.slot == "auto" else a.slot
    chs = [Channel(n) for n in names]
    pv = [float(x) for x in a.preview_times.split(",")] if a.preview_times else None

    if a.check:
        print("skip=" + ("true" if slot and all(c.slot_done(slot) for c in chs) else "false")); return
    if a.list:
        for c in chs:
            for p in c.episodes():
                eid = os.path.basename(p)[:-5]
                print(f"[{c.name}] " + ("✅ " if eid in c.d["sent"] else "❌ " if eid in c.d["failed"] else "⏳ ") + eid)
        return
    if a.autogen:
        for c in chs: run_autogen(c)
        return

    if not pv and not a.no_send:
        for c in chs:
            try: run_inbox(c)
            except Exception as e: print(f"[{c.name}] inbox xato: {e}")
    jobs = []
    for c in chs:
        if slot and c.slot_done(slot):
            print(f"[{c.name}] {slot} sloti bugun yuborilgan — o'tkazildi"); continue
        if a.episode:
            p = os.path.join(c.ep_dir, a.episode + ".json")
            if not os.path.exists(p):
                if len(chs) == 1: raise SystemExit(f"Epizod topilmadi: {p}")
                continue
            job = make_video(c, p, a.quality, a.sponsor, a.no_sponsor, pv)
            if job: job["queued"] = False; jobs.append(job)
            continue
        if not c.queue():
            try: run_autogen(c)
            except Exception as e:
                print(f"[{c.name}] autogen xato: {e}"); telegram.notify(f"AI {c.name}: navbat bo'sh, ssenariy yozishda xato: {e}")
        job = None
        for p in c.queue():
            ep = json.load(open(p, encoding="utf-8"))
            err = check_episode(c, ep)
            if err:
                c.d["failed"].append(ep["id"]); c.save()
                telegram.notify(f"AI {c.name}: {ep['id']} ssenariysida xato, o'tkazib yuborildi: " + "; ".join(err[:4])); continue
            try:
                job = make_video(c, p, a.quality, a.sponsor, a.no_sponsor, pv)
                break
            except Exception as e:
                if ep.get("num", 0) <= 10: raise   # boshlang'ich (tekshirilgan) epizodlar — haqiqiy xato
                c.d["failed"].append(ep["id"]); c.save()
                telegram.notify(f"AI {c.name}: ssenariy {ep['id']} render bo'lmadi ({e}). Keyingisi olinadi.")
        if job: job["queued"] = True; jobs.append(job)
        elif not pv: telegram.notify(f"AI {c.name}: navbatda video yo'q.")

    if a.no_send or not jobs: return
    if a.send_at:
        wait_until(SLOTS.get(slot, "06:00") if a.send_at == "auto" else a.send_at)
    errors = []
    for j in jobs:
        c, ep = j["ch"], j["ep"]
        try:
            telegram.send_manual(j["mp4"], ep, j["caption"], chats(), c.cfg)
        except Exception as e:
            errors.append(f"{c.name}: {e}"); continue
        if j["queued"] or a.mark_sent:
            c.d["sent"] = sorted(set(c.d["sent"]) | {ep["id"]})
            c.d["log"].setdefault(f"{today().isoformat()}_{slot or 'manual'}", []).append(ep["id"])
        if j["sponsor"]:
            c.d["sponsor_counts"][j["sponsor"]["id"]] = c.d["sponsor_counts"].get(j["sponsor"]["id"], 0) + 1
        c.save()
        left = len(c.queue())
        telegram.notify(f"AI {c.name}: {ep['id']} yuborildi. Navbatda qoldi: {left}"
                        + (f"\n📥 Ssenariylar kam qoldi — inbox/{c.name}/ ga yangilarini yuklang." if left in (6, 4, 2) else ""))
        if j["queued"] and left == 0:
            try: run_autogen(c)
            except Exception as e:
                print(f"[{c.name}] autogen xato: {e}"); telegram.notify(f"AI {c.name}: yangi ssenariy yozishda xato: {e}")
    if errors: raise SystemExit("Yuborishda xato: " + "; ".join(errors))

if __name__ == "__main__":
    main()
