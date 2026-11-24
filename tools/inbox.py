"""Qo'lda yuklangan ssenariylarni navbatga qo'shadi.

Claude chat yozgan JSON faylni GitHub'da shu papkaga yuklang:
    inbox/doxtir/   — @ai_doxtir ssenariylari
    inbox/olmaliq/  — @ai_olmaliq ssenariylari
Fayl ichida: bitta epizod {...}, ro'yxat [...] yoki {"episodes": [...]} bo'lishi mumkin.

Har jadval ishida (run.py) avtomatik: tekshiradi → raqam va id beradi → epizodlar papkasiga yozadi →
faylni inbox/<kanal>/done/ ga ko'chiradi → botga natija va ssenariylar matnini yuboradi.
Qo'lda: python tools/inbox.py
"""
import os, re, json, glob, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _slug(s):
    s = re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "").replace("ʻ", "").replace("‘", "")).strip("_")
    return s[:24] or "epizod"

def _items(data):
    if isinstance(data, dict) and "episodes" in data: return data["episodes"]
    if isinstance(data, list): return data
    return [data]

def process(ch):
    """-> (qo'shilgan epizodlar, xatolar ro'yxati)"""
    from tools.autogen import validate, SPECS
    spec = SPECS[ch.name]; box = os.path.join(ROOT, "inbox", ch.name)
    files = sorted(glob.glob(os.path.join(box, "*.json")))
    if not files: return [], []
    nums = [json.load(open(p, encoding="utf-8")).get("num", 0) for p in ch.episodes()]
    num = max(nums + [0]) + 1
    added, errors = [], []
    for f in files:
        name = os.path.basename(f)
        try:
            items = _items(json.load(open(f, encoding="utf-8-sig")))
        except Exception as e:
            errors.append(f"{name}: JSON o'qilmadi ({e})"); continue
        for i, ep in enumerate(items):
            if not isinstance(ep, dict):
                errors.append(f"{name} #{i + 1}: epizod emas"); continue
            ep.setdefault("id", _slug(str(ep.get("title", "epizod"))))
            err = validate(ep, spec)
            if err:
                errors.append(f"{name} #{i + 1} «{ep.get('title', '?')}»: " + "; ".join(err[:4])); continue
            ep.update({"num": num, "series": ep.get("series") or spec["series"], "id": f"{ch.prefix}{num:02d}_{_slug(ep.get('id') or ep['title'])}"})
            ep.setdefault("tags", [])
            if ch.name == "doxtir" and "Ma'lumot uchun" not in ep["instagram"]:
                ep["instagram"] += "\n\n⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi."
            json.dump(ep, open(os.path.join(ch.ep_dir, ep["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            added.append(ep); num += 1
        done = os.path.join(box, "done"); os.makedirs(done, exist_ok=True)
        shutil.move(f, os.path.join(done, dt.datetime.now().strftime("%Y%m%d_%H%M_") + name))
    return added, errors

if __name__ == "__main__":
    import sys; sys.path.insert(0, ROOT)
    import run
    for n in run.CHANNELS:
        a, e = process(run.Channel(n))
        print(f"[{n}] qo'shildi: {[x['id'] for x in a]}"); [print("  xato:", x) for x in e]
