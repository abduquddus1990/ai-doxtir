"""Navbat tugaganda keyingi 10 ta ssenariyni Claude API orqali avtomatik yozadi.

- Mavjud epizodlar namuna sifatida beriladi; yangi epizodlar faqat mavjud 3D quruvchilar va sahna turlaridan foydalanadi.
- Faktlar veb-qidiruv bilan tekshiriladi, manbalari tavsifga yoziladi.
- Natija qat'iy tekshiriladi (validate); xato bo'lsa model bir marta tuzatadi.
- Yangi fayllar epizodlar papkasiga yoziladi ("auto": true), matni botga ko'rib chiqish uchun yuboriladi (run.py).

Kerak: ANTHROPIC_API_KEY (GitHub Secret). Sinov: python run.py --autogen --channel doxtir
"""
import os, re, json, glob

MODEL = "claude-opus-5-5"
BATCH = int(os.environ.get("AUTOGEN_BATCH", "10"))
SCENE_TYPES = {"hook", "cause", "stages", "cta"}
FX = {"label", "ring", "bolts", "glow", "sparkle", "arrow", "sprite", "drops", "cross", "check", "shake"}
COLORS = {"teal", "coral", "amber", "orange", "ink", "blue", "purple", "green", "white", "dentin", "grey", "copper"}

SPECS = {
    "doxtir": {
        "builders": {"section", "wisdom", "front", "molar", "implant_parts", "sprite"},
        "sprites": {"bact_g", "bact_p", "sugar", "soda", "lemon", "brush", "candy"},
        "about": ("@ai_doxtir — stomatologiya (tish salomatligi) haqida 30-40 soniyalik 3D Reels. Auditoriya: Olmaliq shahri aholisi "
                  "(Toshkent viloyati). Til: o'zbek (lotin). Tibbiy ma'lumotlar zamonaviy dalillarga asoslangan, qo'rqitmasdan, "
                  "amaliy maslahat bilan. Hech qachon dori nomi/dozasi yoki uyda davolash usulini tavsiya qilmang; "
                  "har tavsifda '⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi.' qatori bo'lsin."),
        "series": "Tish sirlari",
        "doc": """Quruvchilar (assets[*].build) va parametrlari — FAQAT shular:
- section: tish kesimi (milk, suyak bilan). params: caries 0-3, fill(bool), pulp "normal|hot|gutta|none", gum "normal|red|recede",
  gum_red(bool), bone_drop 0-0.5, tartar 0-2, baby(bool, sut tishi), germ(bool, ostida doimiy tish kurtagi), germ_glow(bool),
  no_tooth(bool, tishsiz joy), implant "screw|abutment|crown" (no_tooth bilan), access(bool), access_fill(bool), files(bool), abscess(bool),
  yellow(bool), enamel_scale, den_scale. Ankerlar: top, crown, enamel, dentin, pulp, gum, bone, car1, car2, car3, canal, root_tip,
  apex_l, apex_r, tartar_l, tartar_r, germ, implant, abut.
- molar: butun oziq tish. params: spot(bool), tartar(bool), yellow(bool). Ankerlar: top, crown. "turn": {"frames":24,"from":-40,"to":120} bilan aylanadi.
- front: old tishlar qatori. params: crooked 0-1, brackets(bool), yellow(bool), white(bool), gel(bool), plaque(bool), gum_red(bool), recession(bool).
  Ankerlar: center, gumline, tooth2, edge, left, right.
- wisdom: aql tishi. params: stage 0-3. Ankerlar: wisdom, neighbor, contact, gum, socket.
- implant_parts: implant qismlari (vint, abatment, toj). Ankerlar: crown, abut, screw. "turn" bilan.
- sprite: params.kind = bact_g|bact_p|sugar|soda|lemon|brush|candy (kichik obyektlar, "samples": 24).""",
    },
    "olmaliq": {
        "builders": {"terrain", "quarry", "ore", "flotation", "globe", "shaft", "osprite"},
        "sprites": {"apple", "truck", "cathode", "wire", "gold", "silver", "helmet", "phone", "nugget"},
        "about": ("@ai_olmaliq — faqat Olmaliq shahri haqida 30-40 soniyalik 3D Reels: tarix, geografiya, kon-metallurgiya kombinati, "
                  "kasblar, shahar hayoti, tabiat, kelajak rejalari. Auditoriya: Olmaliq aholisi. Til: o'zbek (lotin). "
                  "FAKTLAR: faqat veb-qidiruvda ishonchli manbada (rasmiy saytlar, yirik OAV, ensiklopediya) tasdiqlanganini yozing; "
                  "aniq raqamni faqat manbada ko'rsangiz yozing, aks holda raqamsiz yozing. Har tavsifda 'Manba: ...' qatori bo'lsin. "
                  "Siyosat, mish-mish, shaxslar haqida salbiy gap, kombinat logotipi — yo'q."),
        "series": "Olmaliq sirlari",
        "doc": None,  # engine/olmaliq3d.py docstring
    },
}

SCHEMA_DOC = """Epizod JSON tuzilishi (namunalardagidek):
{"id": "<slug>", "num": <int>, "series": "...", "title": "...", "tags": [...],
 "assets": {"<nom>": {"build": "<quruvchi>", "params": {...}, "turn"?: {...}, "samples"?: 24}, ...},   // 4-8 ta asset
 "scenes": [
   {"type": "hook", "dur": 3.4, "img": "<asset>", "pos": [540, 1160], "zoom": [1.0, 1.15], "center": "<anker>", "lines": [[matn, o'lcham, rang?, kechikish?], ...]},
   {"type": "cause", ...}?,                       // ixtiyoriy: falling/crawlers — sprite asset nomlari
   {"type": "stages", "steps": [{"img": "<asset>", "dur": 4.0, "view": [masshtab, "<anker>"], "badge": ["MATN", "<rang>"], "lines": [...], "fx": [...]}, ...]},  // 3-5 qadam
   {"type": "cta", "dur": 4.6, "img": "<asset>", "pos": [540, 980], "scale": 0.9, "center": "<anker>", "lines": [...]}],
 "instagram": "<tavsif: hook, mazmun, 💬 savol, 📍 Olmaliq, (disclaimer yoki Manba), heshteglar>",
 "sources": ["<manba sayt/sarlavha>", ...]}
Qoidalar: ekrandagi matnda *yulduzcha* ichidagi so'z rangli ajratiladi; ekrandagi matnda emoji YO'Q; bir qator <= 26 belgi;
ranglar: teal coral amber orange ink blue purple green grey copper dentin; fx turlari: label ring bolts glow sparkle arrow sprite drops cross check shake;
label: {"kind":"label","at":"<anker>","text":"..","color":"..","to":[x,y],"side":"left|right","delay":1.0} (x 250-830, y 650-1300);
umumiy davomiylik 25-40 s. Har asset render ~1 daqiqa, shuning uchun bir xil assetni qayta ishlating."""

def _spec(ch):
    s = dict(SPECS[ch.name])
    if s["doc"] is None:
        from engine import olmaliq3d  # bpy importi faqat build vaqtida — bu yerda docstring kerak
        s["doc"] = olmaliq3d.__doc__
    return s

def _examples(ch, n=4):
    eps = [json.load(open(p, encoding="utf-8")) for p in ch.episodes()]
    return eps, [e for e in eps if not e.get("auto")][:n] or eps[:n]

def validate(ep, spec, assets_ok=True):
    err = []
    for k in ("id", "title", "assets", "scenes", "instagram"):
        if k not in ep: err.append(f"{k} yo'q")
    if err: return err
    A = ep["assets"]
    if not isinstance(A, dict) or not (2 <= len(A) <= 10): err.append("assets 2-10 ta bo'lsin")
    for n, a in A.items():
        b = a.get("build")
        if b not in spec["builders"]: err.append(f"asset {n}: noma'lum build {b}")
        if b in ("sprite", "osprite") and a.get("params", {}).get("kind") not in spec["sprites"]: err.append(f"asset {n}: noma'lum kind")
    def img(x, where):
        if x not in A: err.append(f"{where}: '{x}' asset yo'q")
    def lines(ls, where):
        if not isinstance(ls, list) or not ls: err.append(f"{where}: lines bo'sh"); return
        for l in ls:
            if not (isinstance(l, list) and l and isinstance(l[0], str)): err.append(f"{where}: lines formati"); continue
            if len(l) > 1 and not isinstance(l[1], (int, float)): err.append(f"{where}: o'lcham son bo'lsin")
            if len(l) > 2 and l[2] not in COLORS: err.append(f"{where}: rang {l[2]}")
            if len(l[0].replace("*", "")) > 34: err.append(f"{where}: qator juda uzun: {l[0]}")
    S = ep["scenes"]; total = 0
    if not S or S[0].get("type") != "hook" or S[-1].get("type") != "cta": err.append("birinchi sahna hook, oxirgisi cta bo'lsin")
    for i, sc in enumerate(S):
        t = sc.get("type"); w = f"scene{i}:{t}"
        if t not in SCENE_TYPES: err.append(f"{w}: noma'lum tur"); continue
        if t == "stages":
            st = sc.get("steps", [])
            if not (2 <= len(st) <= 6): err.append(f"{w}: 2-6 qadam")
            for j, s in enumerate(st):
                img(s.get("img"), f"{w}.step{j}"); lines(s.get("lines"), f"{w}.step{j}"); total += float(s.get("dur", 0))
                if s.get("badge") and (len(s["badge"]) != 2 or s["badge"][1] not in COLORS): err.append(f"{w}.step{j}: badge")
                for f in s.get("fx", []):
                    if f.get("kind") not in FX: err.append(f"{w}.step{j}: fx {f.get('kind')}")
                    if f.get("kind") == "sprite": img(f.get("name"), f"{w}.step{j}.fx")
                    if f.get("kind") == "label" and not (isinstance(f.get("to"), list) and len(f["to"]) == 2): err.append(f"{w}.step{j}: label.to")
        else:
            img(sc.get("img"), w); lines(sc.get("lines"), w); total += float(sc.get("dur", 0))
            for n in sc.get("falling", []) + sc.get("crawlers", []): img(n, w + ".sprite")
    if not (20 <= total <= 48): err.append(f"davomiylik {total:.1f}s (25-40 bo'lsin)")
    return err

def _slug(s):
    s = re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "").replace("ʻ", "")).strip("_")
    return s[:24] or "epizod"

def _extract_json(text):
    m = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = m[-1] if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(raw)

def _call(client, system, messages):
    import anthropic
    kw = dict(model=MODEL, max_tokens=64000, system=system, messages=messages,
              thinking={"type": "adaptive"}, output_config={"effort": "high"},
              tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 20}])
    for _ in range(6):
        try:
            with client.beta.messages.stream(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kw) as st:
                msg = st.get_final_message()
        except TypeError:  # eski SDK: fallbacks parametri yo'q
            with client.messages.stream(**kw) as st:
                msg = st.get_final_message()
        if msg.stop_reason == "refusal":
            raise RuntimeError("model rad etdi (refusal)")
        if msg.stop_reason == "pause_turn":
            kw["messages"] = kw["messages"] + [{"role": "assistant", "content": msg.content}]; continue
        return msg
    raise RuntimeError("pause_turn tsikli tugamadi")

def generate(ch):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY kiritilmagan (GitHub Secret)")
    import anthropic
    spec = _spec(ch); all_eps, ex = _examples(ch)
    start = max([e.get("num", 0) for e in all_eps] + [0]) + 1
    used = "\n".join(f"- #{e.get('num')}: {e['title']}" for e in all_eps)
    system = (f"Siz {spec['about']}\n\nSiz video dvigateli uchun epizod JSON fayllarini yozasiz. Dvigatel faqat quyidagilarni tushunadi.\n\n"
              f"{spec['doc']}\n\n{SCHEMA_DOC}")
    user = (f"Oldingi epizodlar (takrorlamang, yangi mavzular tanlang):\n{used}\n\n"
            f"Namuna epizodlar (format va uslub uchun):\n```json\n{json.dumps(ex, ensure_ascii=False)}\n```\n\n"
            f"Vazifa: #{start}–#{start + BATCH - 1} raqamli {BATCH} ta YANGI epizod yozing (series: \"{spec['series']}\"). "
            f"Avval faktlarni veb-qidiruvda tekshiring. Javob oxirida bitta ```json blokida {{\"episodes\": [...]}} qaytaring.")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user}]
    for attempt in range(2):
        msg = _call(client, system, messages)
        text = "".join(b.text for b in msg.content if b.type == "text")
        try:
            eps = _extract_json(text)["episodes"]; errs = {}
        except Exception as e:
            eps, errs = [], {"json": [str(e)]}
        for i, ep in enumerate(eps):
            e = validate(ep, spec)
            if e: errs[f"#{i + 1} {ep.get('title', '?')}"] = e
        if not errs and len(eps) >= max(1, BATCH // 2): break
        messages += [{"role": "assistant", "content": msg.content},
                     {"role": "user", "content": "Tekshiruvda xatolar topildi, tuzatib to'liq JSON'ni qayta yuboring:\n" + json.dumps(errs, ensure_ascii=False)}]
    good = [ep for ep in eps if not validate(ep, spec)]
    if not good: raise RuntimeError(f"yaroqli ssenariy chiqmadi: {list(errs.items())[:3]}")
    out = []
    for k, ep in enumerate(good):
        num = start + k
        ep.update({"num": num, "series": spec["series"], "auto": True, "id": f"{ch.prefix}{num:02d}_{_slug(ep.get('id') or ep['title'])}"})
        ep.setdefault("tags", [])
        if ch.name == "doxtir" and "Ma'lumot uchun" not in ep["instagram"]:
            ep["instagram"] += "\n\n⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi."
        json.dump(ep, open(os.path.join(ch.ep_dir, ep["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        out.append(ep)
    print(f"[{ch.name}] {len(out)} ta yangi ssenariy yozildi: {[e['id'] for e in out]}")
    return out

def review_text(ch, eps):
    head = f"📝 {ch.cfg.get('bot_head', ch.name)}: keyingi {len(eps)} ta ssenariy (#{eps[0]['num']}–#{eps[-1]['num']}) navbatga qo'shildi. Tanishib chiqing."
    parts = [head]
    for ep in eps:
        screen = []
        for sc in ep["scenes"]:
            for s in (sc.get("steps") or [sc]):
                screen.append(" ".join(l[0].replace("*", "") for l in s.get("lines", [])))
        src = ", ".join(ep.get("sources", []))
        parts.append(f"#{ep['num']} {ep['title']}\n🎬 Ekranda: " + " → ".join(screen) + f"\n\n📄 Tavsif:\n{ep['instagram']}" + (f"\n\n🔎 Manbalar: {src}" if src else ""))
    parts.append("O'zgartirish yoki olib tashlash kerak bo'lsa, GitHub'da fayllarni tahrirlang yoki Claude'ga ayting.")
    return "\n\n".join(parts)
