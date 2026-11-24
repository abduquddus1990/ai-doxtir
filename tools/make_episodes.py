"""10 ta boshlang'ich epizod JSON fayllarini yozadi (episodes/). Matnlarni o'zgartirish uchun JSON'ni to'g'ridan-to'g'ri tahrirlash ham mumkin."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "episodes")
SPR = {k: {"build": "sprite", "params": {"kind": k}, "samples": 24} for k in ("bact_g", "bact_p", "sugar", "soda", "lemon", "brush", "candy")}
def sec(**p): return {"build": "section", "params": p}
def front(**p): return {"build": "front", "params": p}
def L(text, size=72, acc="teal", delay=None):
    x = [text, size, acc]
    if delay is not None: x.append(delay)
    return x
TAGS = "#olmaliq #almalyk #toshkentviloyati #stomatologiya #tishlar #sogliq #3d #ai_doxtir"
DISC = "⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi."

EP = []

# ---------------------------------------------------------------- 1 karies
EP.append({
 "id": "e01_karies", "num": 1, "series": "Tish sirlari", "title": "Karies tishni qanday yeydi",
 "assets": {"turn": {"build": "molar", "params": {"spot": True}, "turn": {"frames": 24, "from": -40, "to": 120}},
            "healthy": {"build": "molar", "params": {}}, "bact_g": SPR["bact_g"], "bact_p": SPR["bact_p"], "sugar": SPR["sugar"],
            "s0": sec(), "s1": sec(caries=1), "s2": sec(caries=2), "s3": sec(caries=3, pulp="hot"), "s4": sec(caries=2, fill=True)},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "turn", "pos": [540, 1150], "zoom": [1.0, 1.2], "ring": [540, 790],
   "lines": [L("Shu *kichkina nuqta*", 84), L("tishingizni ichidan", 70), L("*yeb qo'yadi*", 92, "coral")]},
  {"type": "cause", "dur": 5.2, "img": "turn", "pos": [540, 1320], "scale": 1.0, "falling": ["sugar", "sugar", "sugar"],
   "crawlers": ["bact_g", "bact_p", "bact_p", "bact_g"], "drops": "#aae63c",
   "lines": [L("Shakar + bakteriya", 76), L("= *kislota*", 92, "coral", 2.2)]},
  {"type": "stages", "steps": [
   {"img": "s0", "dur": 3.8, "view": [1.2, "crown"], "badge": ["TISH ICHIDA", "teal"], "lines": [L("3 qavatdan iborat", 76)],
    "fx": [{"kind": "label", "at": "enamel", "text": "Emal", "color": "teal", "to": [330, 700], "delay": 0.9},
           {"kind": "label", "at": "dentin", "text": "Dentin", "color": "dentin", "to": [330, 930], "delay": 1.5},
           {"kind": "label", "at": "pulp", "text": "Pulpa (nerv)", "color": "coral", "to": [760, 800], "side": "right", "delay": 2.1}]},
   {"img": "s1", "dur": 4.2, "view": [2.0, "crown"], "badge": ["1-BOSQICH · EMAL", "amber"],
    "lines": [L("Og'rimaydi, shuning uchun", 64), L("*sezilmaydi*", 84, "amber")], "fx": [{"kind": "ring", "at": "car1", "color": "amber", "delay": 1.2}]},
   {"img": "s2", "dur": 4.4, "view": [2.0, "crown"], "badge": ["2-BOSQICH · DENTIN", "orange"],
    "lines": [L("Shirin va sovuqdan", 66), L("*sanchiq* paydo bo'ladi", 74, "orange")], "fx": [{"kind": "bolts", "at": "car2", "color": "orange"}]},
   {"img": "s3", "dur": 4.8, "view": [1.55, "pulp"], "badge": ["3-BOSQICH · PULPA", "coral"],
    "lines": [L("Kuchli og'riq —", 72), L("*kanal davolash* kerak", 70, "coral")],
    "fx": [{"kind": "glow", "at": "pulp", "dy": 40, "delay": 0.8}, {"kind": "bolts", "at": "pulp", "color": "coral", "r": 250, "size": 58, "n": 5}, {"kind": "shake"}]},
   {"img": "s4", "dur": 4.4, "view": [2.0, "crown"], "badge": ["YECHIM", "teal"],
    "lines": [L("Erta aniqlansa —", 72), L("*bitta tashrif*, plomba", 70)], "fx": [{"kind": "sparkle", "at": "car2"}]}]},
  {"type": "cta", "dur": 4.8, "img": "healthy", "pos": [540, 900], "scale": 0.95, "center": "crown",
   "lines": [L("Har *6 oyda*", 84), L("stomatolog ko'rigidan o'ting", 58)]}],
 "instagram": "Shu kichkina qora nuqta tishingizni ichidan yeb qo'yadi 🦷\n\nKaries 3 bosqichda rivojlanadi: avval emalda (og'rimaydi), keyin dentinda (shirin va sovuqdan sanchiydi), oxiri pulpada — kuchli og'riq va kanal davolash. Erta aniqlansa, oddiy plomba yetarli.\n\n💬 Oxirgi marta stomatologga qachon borgansiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS,
})

# ---------------------------------------------------------------- 2 tish toshi
EP.append({
 "id": "e02_tish_toshi", "num": 2, "series": "Tish sirlari", "title": "Milk nega qonaydi: tish toshi",
 "assets": {"hero": {"build": "molar", "params": {"tartar": True}}, "bact_g": SPR["bact_g"], "bact_p": SPR["bact_p"], "candy": SPR["candy"],
            "g0": sec(), "g1": sec(tartar=1), "g2": sec(tartar=2, gum="red"), "g3": sec(tartar=2, gum="recede", gum_red=True, bone_drop=0.35), "g4": sec()},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "hero", "pos": [540, 1170], "zoom": [1.05, 1.2], "center": "crown",
   "lines": [L("Milk *qonayaptimi*?", 84, "coral"), L("Bu tish toshining", 66), L("*birinchi signali*", 84, "coral")]},
  {"type": "cause", "dur": 4.8, "img": "hero", "pos": [540, 1330], "scale": 1.0, "center": "crown", "falling": ["candy", "candy"],
   "crawlers": ["bact_g", "bact_p", "bact_g", "bact_p"], "eat": False,
   "lines": [L("Ovqat qoldig'i + bakteriya", 62), L("= *karash*", 88, "amber", 2.0)]},
  {"type": "stages", "steps": [
   {"img": "g0", "dur": 3.4, "view": [1.4, "crown"], "badge": ["SOG'LOM MILK", "teal"], "lines": [L("Milk tishni *mahkam* quchoqlaydi", 60)],
    "fx": [{"kind": "label", "at": "gum", "text": "Milk", "color": "coral", "to": [300, 760], "delay": 0.8},
           {"kind": "label", "at": "bone", "text": "Suyak", "color": "dentin", "to": [300, 1150], "delay": 1.3}]},
   {"img": "g1", "dur": 4.0, "view": [1.6, "crown"], "badge": ["1 · KARASH", "amber"],
    "lines": [L("Yumshoq qatlam —", 70), L("*cho'tka bilan* ketadi", 70, "amber")], "fx": [{"kind": "ring", "at": "tartar_r", "color": "amber", "r": 80}]},
   {"img": "g2", "dur": 4.4, "view": [1.6, "crown"], "badge": ["2 · TISH TOSHI", "orange"],
    "lines": [L("Qotib *toshga* aylanadi,", 66, "orange"), L("milk qizarib qonaydi", 62)],
    "fx": [{"kind": "ring", "at": "tartar_r", "color": "orange", "r": 80}, {"kind": "glow", "at": "gum", "color": "coral", "r": 140, "delay": 1.4}]},
   {"img": "g3", "dur": 4.6, "view": [1.4, "crown"], "badge": ["3 · PARODONTIT", "coral"],
    "lines": [L("Milk va suyak *pasayadi*", 66, "coral"), L("tish qimirlay boshlaydi", 62)],
    "fx": [{"kind": "arrow", "from": "tartar_r", "at": "bone", "color": "coral"}, {"kind": "shake"}]},
   {"img": "g4", "dur": 4.2, "view": [1.6, "crown"], "badge": ["YECHIM", "teal"],
    "lines": [L("*Professional tozalash*", 70), L("yiliga 1–2 marta", 64)], "fx": [{"kind": "sparkle", "at": "tartar_r"}]}]},
  {"type": "cta", "dur": 4.6, "img": "g4", "pos": [540, 980], "scale": 1.0, "center": "crown",
   "lines": [L("Tishni *kuniga 2 marta*", 74), L("va tish ipi bilan tozalang", 58)]}],
 "instagram": "Tish yuvganda milk qonaydimi? Bu — tish toshining birinchi signali 🩸\n\nYumshoq karash vaqtida tozalanmasa, qotib toshga aylanadi. Tosh milkni qizartiradi, keyin milk va suyak pasayib, tish qimirlay boshlaydi (parodontit). Toshni faqat stomatolog professional tozalash bilan oladi.\n\n💬 Sizda ham milk qonaganmi?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #parodontit",
})

# ---------------------------------------------------------------- 3 implant
EP.append({
 "id": "e03_implant", "num": 3, "series": "Tish sirlari", "title": "Implant qanday qo'yiladi",
 "assets": {"parts": {"build": "implant_parts", "params": {}, "turn": {"frames": 24, "from": -70, "to": 60, "tilt": 8}},
            "i0": sec(no_tooth=True), "i1": sec(no_tooth=True, implant="screw"), "i2": sec(no_tooth=True, implant="abutment"), "i3": sec(no_tooth=True, implant="crown")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "parts", "pos": [540, 1170], "zoom": [1.0, 1.15],
   "lines": [L("Tishsiz qoldingizmi?", 76), L("*Implant* qanday", 86), L("qo'yiladi — 3D'da", 66)]},
  {"type": "stages", "steps": [
   {"img": "i0", "dur": 4.0, "view": [1.35, "abut"], "badge": ["1 · BO'SH JOY", "amber"],
    "lines": [L("Tish yo'q joyda", 70), L("suyak *yupqalashadi*", 72, "amber")], "fx": [{"kind": "ring", "at": "implant", "color": "amber", "r": 120}]},
   {"img": "i1", "dur": 4.4, "view": [1.35, "abut"], "badge": ["2 · TITAN VINT", "blue"],
    "lines": [L("Vint *suyakka*", 76, "blue"), L("o'rnatiladi", 70)],
    "fx": [{"kind": "label", "at": "implant", "text": "Titan", "color": "blue", "to": [800, 1180], "side": "right", "delay": 1.0}]},
   {"img": "i2", "dur": 4.4, "view": [1.35, "abut"], "badge": ["3 · BITISH", "teal"],
    "lines": [L("Bir necha oyda suyak", 66), L("vintni *mahkam* ushlaydi", 68)],
    "fx": [{"kind": "label", "at": "abut", "text": "Abatment", "color": "teal", "to": [800, 900], "side": "right", "delay": 1.0}]},
   {"img": "i3", "dur": 4.4, "view": [1.35, "abut"], "badge": ["4 · TOJ", "teal"],
    "lines": [L("Ustiga *toj* qo'yiladi", 74), L("xuddi o'z tishingizdek", 62)], "fx": [{"kind": "sparkle", "at": "crown"}]}]},
  {"type": "cta", "dur": 4.6, "img": "parts", "pos": [540, 930], "scale": 0.9,
   "lines": [L("Implant sizga mosmi —", 66), L("*shifokor* aniqlaydi", 74)]}],
 "instagram": "Implant qanday qo'yiladi — 3D'da ko'ring 🦷\n\n1️⃣ Tish yo'q joyda vaqt o'tishi bilan suyak yupqalashadi\n2️⃣ Titan vint suyakka o'rnatiladi\n3️⃣ Bir necha oy ichida suyak vintni mahkam ushlab oladi\n4️⃣ Ustiga abatment va toj qo'yiladi\n\nImplant hammaga ham mos emas — buni shifokor tekshiruvdan keyin aytadi.\n\n💬 Implant haqida qanday savolingiz bor?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #implant",
})

# ---------------------------------------------------------------- 4 breket
EP.append({
 "id": "e04_breket", "num": 4, "series": "Tish sirlari", "title": "Breket tishni qanday suradi",
 "assets": {"b0": front(crooked=1.0), "b1": front(crooked=1.0, brackets=True), "b2": front(crooked=0.5, brackets=True),
            "b3": front(crooked=0.0, brackets=True), "b4": front(crooked=0.0, white=True)},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "b0", "pos": [540, 1150], "zoom": [0.92, 1.02], "center": "center",
   "lines": [L("Qiyshiq tishlar", 82), L("*qanday* to'g'rilanadi?", 76)]},
  {"type": "stages", "steps": [
   {"img": "b1", "dur": 4.2, "view": [0.95, "center"], "badge": ["1 · BREKET", "blue"],
    "lines": [L("Har tishga *qulf*", 76, "blue"), L("ular sim bilan bog'lanadi", 60)],
    "fx": [{"kind": "label", "at": "center", "text": "Sim", "color": "blue", "to": [820, 1300], "side": "right", "delay": 1.2}]},
   {"img": "b2", "dur": 4.6, "view": [0.95, "center"], "badge": ["2 · YENGIL BOSIM", "orange"],
    "lines": [L("Sim tishlarni", 70), L("*sekin-asta* suradi", 76, "orange")],
    "fx": [{"kind": "arrow", "from": "left", "at": "tooth2", "color": "orange"}]},
   {"img": "b3", "dur": 4.4, "view": [0.95, "center"], "badge": ["3 · NATIJA", "teal"],
    "lines": [L("Odatda *1–2 yil*", 78), L("davom etadi", 64)]},
   {"img": "b4", "dur": 4.2, "view": [0.95, "center"], "badge": ["TEKIS TISHLAR", "teal"],
    "lines": [L("Chiroyli va", 70), L("*tozalash oson*", 80)], "fx": [{"kind": "sparkle", "at": "center"}]}]},
  {"type": "cta", "dur": 4.6, "img": "b4", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Breket kerakmi —", 70), L("*ortodont* aniqlaydi", 76)]}],
 "instagram": "Breket tishni qanday suradi? 🦷\n\nHar bir tishga kichik qulf (breket) yopishtiriladi, ular sim bilan bog'lanadi. Sim tishlarga doimiy yengil bosim berib, ularni sekin-asta to'g'ri joyga suradi. Davolash odatda 1–2 yil davom etadi — aniq muddatni ortodont belgilaydi.\n\n💬 Breket taqqanmisiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #breket #ortodont",
})

# ---------------------------------------------------------------- 5 oqartirish
EP.append({
 "id": "e05_oqartirish", "num": 5, "series": "Tish sirlari", "title": "Tishni oqartirish: soda va limon xavfi",
 "assets": {"w0": front(yellow=True), "w1": sec(enamel_scale=0.9, den_scale=0.86), "w2": front(yellow=True, gel=True),
            "w3": front(white=True), "lemon": SPR["lemon"]},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "w0", "pos": [540, 1170], "zoom": [0.92, 1.02], "center": "center",
   "lines": [L("Tishlar *sarg'aydimi*?", 78, "amber"), L("Soda va limon", 70), L("*yordam bermaydi*", 80, "coral")]},
  {"type": "stages", "steps": [
   {"img": "w0", "dur": 3.8, "view": [0.95, "center"], "badge": ["SABABI", "amber"], "enter": False,
    "lines": [L("Choy, qahva, sigaret", 68), L("*dog'* qoldiradi", 82, "amber")]},
   {"img": "w1", "dur": 4.6, "view": [2.0, "crown"], "badge": ["XATO USUL", "coral"],
    "lines": [L("Soda va limon", 70), L("*emalni yemiradi*", 76, "coral")],
    "fx": [{"kind": "sprite", "name": "lemon", "at": "top", "path": "fall", "scale": 0.5, "dy": -230, "delay": 0.6},
           {"kind": "bolts", "at": "enamel", "color": "coral", "delay": 1.6}]},
   {"img": "w2", "dur": 4.4, "view": [0.95, "center"], "badge": ["TO'G'RI USUL", "teal"],
    "lines": [L("*Professional gel*", 78), L("shifokor nazoratida", 62)]},
   {"img": "w3", "dur": 4.2, "view": [0.95, "center"], "badge": ["NATIJA", "teal"],
    "lines": [L("Oq va *xavfsiz*", 84)], "fx": [{"kind": "sparkle", "at": "center"}]}]},
  {"type": "cta", "dur": 4.6, "img": "w3", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Oqartirishdan oldin", 70), L("*stomatologga* ko'rining", 70)]}],
 "instagram": "Tishlar sarg'aydimi? Soda va limon yordam bermaydi ⚠️\n\nChoy, qahva va sigaret tishda dog' qoldiradi. Uyda soda yoki limon bilan ishqalash emalni yemiradi — emal esa qayta tiklanmaydi. Xavfsiz yo'l — shifokor nazoratidagi professional oqartirish.\n\n💬 Uyda oqartirishni sinab ko'rganmisiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #oqartirish",
})

# ---------------------------------------------------------------- 6 kanal
EP.append({
 "id": "e06_kanal", "num": 6, "series": "Tish sirlari", "title": "Kanal davolash ichidan",
 "assets": {"k0": sec(caries=3, pulp="hot", abscess=True), "k1": sec(access=True, files=True, pulp="hot"),
            "k2": sec(access=True, pulp="gutta"), "k3": sec(access=True, access_fill=True, pulp="gutta")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "k0", "pos": [540, 1150], "zoom": [1.3, 1.5], "center": "pulp",
   "lines": [L("Tish *zirqirab*", 84, "coral"), L("og'riyaptimi?", 76), L("Kanal davolash — ichidan", 58)]},
  {"type": "stages", "steps": [
   {"img": "k0", "dur": 4.2, "view": [1.25, "pulp"], "badge": ["MUAMMO", "coral"], "enter": False,
    "lines": [L("Infeksiya *nervga*", 74, "coral"), L("va ildiz uchiga yetgan", 62)],
    "fx": [{"kind": "glow", "at": "pulp", "dy": 30, "delay": 0.6}, {"kind": "glow", "at": "apex_l", "r": 110, "delay": 1.0},
           {"kind": "glow", "at": "apex_r", "r": 110, "delay": 1.2}, {"kind": "shake"}]},
   {"img": "k1", "dur": 4.6, "view": [1.25, "pulp"], "badge": ["1 · TOZALASH", "blue"],
    "lines": [L("Maxsus *ignalar* bilan", 70, "blue"), L("kanallar tozalanadi", 64)]},
   {"img": "k2", "dur": 4.4, "view": [1.25, "pulp"], "badge": ["2 · TO'LDIRISH", "orange"],
    "lines": [L("Kanallar *germetik*", 72, "orange"), L("to'ldiriladi", 66)],
    "fx": [{"kind": "label", "at": "canal", "text": "Plomba", "color": "orange", "to": [820, 1150], "side": "right", "delay": 1.0}]},
   {"img": "k3", "dur": 4.4, "view": [1.6, "crown"], "badge": ["3 · TIKLASH", "teal"],
    "lines": [L("Tish *saqlab qolinadi*", 72), L("sug'urib tashlanmaydi", 62)], "fx": [{"kind": "sparkle", "at": "top"}]}]},
  {"type": "cta", "dur": 4.6, "img": "k3", "pos": [540, 1000], "scale": 1.1, "center": "crown",
   "lines": [L("Og'riqni *kutib* o'tirmang", 68, "coral")]}],
 "instagram": "Tish zirqirab og'riyaptimi? Kanal davolash ichidan qanday ko'rinadi 🦷\n\nKaries chuqurlashib nervga (pulpaga) yetsa, infeksiya ildiz uchiga tushadi. Shifokor maxsus asboblar bilan kanallarni tozalaydi, germetik to'ldiradi va tishni tiklaydi. Natijada tish sug'urilmasdan saqlab qolinadi.\n\n💬 Kanal davolatganmisiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #kanaldavolash",
})

# ---------------------------------------------------------------- 7 aql tishi
EP.append({
 "id": "e07_aql_tishi", "num": 7, "series": "Tish sirlari", "title": "Aql tishi nega muammo",
 "assets": {"a0": {"build": "wisdom", "params": {"stage": 0}}, "a1": {"build": "wisdom", "params": {"stage": 1}},
            "a2": {"build": "wisdom", "params": {"stage": 2}}, "a3": {"build": "wisdom", "params": {"stage": 3}}},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "a0", "pos": [540, 1150], "zoom": [1.2, 1.4], "center": "contact",
   "lines": [L("*Aql tishi*", 92, "amber"), L("nega muammo", 74), L("keltiradi?", 74)]},
  {"type": "stages", "steps": [
   {"img": "a0", "dur": 4.4, "view": [1.25, "contact"], "badge": ["QIYSHIQ O'SISH", "amber"], "enter": False,
    "lines": [L("Joy yetmasa —", 72), L("*qo'shni tishni* itaradi", 66, "amber")],
    "fx": [{"kind": "arrow", "from": "wisdom", "at": "contact", "color": "coral"}, {"kind": "ring", "at": "contact", "color": "amber", "r": 80, "delay": 1.6}]},
   {"img": "a1", "dur": 4.4, "view": [1.25, "contact"], "badge": ["YALLIG'LANISH", "coral"],
    "lines": [L("Milk *shishadi*,", 76, "coral"), L("og'iz ochish qiyinlashadi", 60)],
    "fx": [{"kind": "glow", "at": "gum", "r": 150}, {"kind": "bolts", "at": "gum", "color": "coral", "r": 170}, {"kind": "shake"}]},
   {"img": "a2", "dur": 4.2, "view": [1.25, "contact"], "badge": ["YECHIM", "teal"],
    "lines": [L("Vaqtida *olib tashlash*", 70), L("qo'shni tishni asraydi", 62)], "fx": [{"kind": "check", "at": "socket", "delay": 1.2}]},
   {"img": "a3", "dur": 4.0, "view": [1.25, "contact"], "badge": ["NATIJA", "teal"],
    "lines": [L("Suyak *tiklanadi*", 80), L("og'riq yo'qoladi", 64)], "fx": [{"kind": "sparkle", "at": "socket"}]}]},
  {"type": "cta", "dur": 4.6, "img": "a3", "pos": [540, 1000], "scale": 1.1, "center": "contact",
   "lines": [L("Aql tishi og'risa —", 70), L("*rentgen* qildiring", 76)]}],
 "instagram": "Aql tishi nega muammo keltiradi? 🦷\n\nJag'da joy yetmasa, aql tishi qiyshiq o'sib qo'shni tishni itaradi. Ustidagi milk yallig'lanib shishadi, og'iz ochish qiyinlashadi. Shifokor rentgenga qarab, uni olib tashlash kerakmi — shuni aniqlaydi.\n\n💬 Aql tishingiz chiqqanmi?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #aqltishi",
})

# ---------------------------------------------------------------- 8 sut tishi
EP.append({
 "id": "e08_sut_tishi", "num": 8, "series": "Tish sirlari", "title": "Sut tishini nega davolash kerak",
 "assets": {"m0": sec(baby=True, germ=True), "m1": sec(baby=True, germ=True, caries=2), "m2": sec(baby=True, germ=True, caries=3, pulp="hot", germ_glow=True),
            "m3": sec(baby=True, germ=True, caries=2, fill=True), "candy": SPR["candy"], "bact_g": SPR["bact_g"], "bact_p": SPR["bact_p"]},
 "scenes": [
  {"type": "hook", "dur": 3.8, "img": "m0", "pos": [540, 1160], "zoom": [1.3, 1.5], "center": "crown",
   "lines": [L("Sut tishi baribir", 72), L("*tushib ketadi*-ku?", 80, "amber"), L("Unda nega davolash kerak", 56)]},
  {"type": "stages", "steps": [
   {"img": "m0", "dur": 4.0, "view": [1.1, "germ"], "badge": ["ICHIDA NIMA BOR", "teal"], "enter": False,
    "lines": [L("Ostida *doimiy tish*", 74), L("o'sib kelyapti", 66)],
    "fx": [{"kind": "label", "at": "germ", "text": "Doimiy tish", "color": "teal", "to": [700, 1250], "side": "right", "delay": 0.8}]},
   {"img": "m1", "dur": 4.2, "view": [1.6, "crown"], "badge": ["KARIES", "amber"],
    "lines": [L("Sut tishida emal *yupqa*,", 64, "amber"), L("karies tez chuqurlashadi", 60)],
    "fx": [{"kind": "ring", "at": "car2", "color": "amber", "r": 80}, {"kind": "sprite", "name": "candy", "at": "top", "path": "fall", "scale": 0.4, "dx": 260, "dy": -150, "delay": 0.4}]},
   {"img": "m2", "dur": 4.6, "view": [1.1, "germ"], "badge": ["XAVF", "coral"],
    "lines": [L("Infeksiya *doimiy tishga*", 68, "coral"), L("zarar yetkazishi mumkin", 62)],
    "fx": [{"kind": "glow", "at": "germ", "r": 170, "delay": 0.8}, {"kind": "shake"}]},
   {"img": "m3", "dur": 4.2, "view": [1.6, "crown"], "badge": ["YECHIM", "teal"],
    "lines": [L("Sut tishini ham", 72), L("*vaqtida davolang*", 78)], "fx": [{"kind": "sparkle", "at": "car2"}]}]},
  {"type": "cta", "dur": 4.6, "img": "m3", "pos": [540, 1000], "scale": 1.2, "center": "crown",
   "lines": [L("Bolani *har 6 oyda*", 74), L("stomatologga olib boring", 60)]}],
 "instagram": "\"Sut tishi baribir tushib ketadi\" — bu xato fikr ⚠️\n\nSut tishi ostida doimiy tish o'sib kelyapti. Sut tishida emal yupqa, shuning uchun karies tez chuqurlashadi. Infeksiya ildiz atrofiga tushsa, ostidagi doimiy tishga ham zarar yetkazishi mumkin.\n\n💬 Farzandingiz oxirgi marta stomatologda qachon bo'lgan?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #bolalarstomatologiyasi",
})

# ---------------------------------------------------------------- 9 tish yuvish
EP.append({
 "id": "e09_tish_yuvish", "num": 9, "series": "Tish sirlari", "title": "Tishni to'g'ri yuvish",
 "assets": {"p0": front(plaque=True), "p1": front(recession=True, gum_red=True), "p2": front(white=True), "brush": SPR["brush"]},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "p0", "pos": [540, 1160], "zoom": [0.92, 1.02], "center": "center",
   "lines": [L("Tishni *to'g'ri*", 84), L("yuvasizmi?", 76), L("Ko'pchilik *xato* qiladi", 66, "coral")]},
  {"type": "stages", "steps": [
   {"img": "p0", "dur": 4.4, "view": [0.95, "center"], "badge": ["XATO", "coral"], "enter": False,
    "lines": [L("Qattiq bosib", 72), L("*u yoq-bu yoqqa* ishqalash", 62, "coral")],
    "fx": [{"kind": "sprite", "name": "brush", "at": "center", "path": "scrub", "scale": 0.75, "dy": 40, "delay": 0.4}]},
   {"img": "p1", "dur": 4.4, "view": [0.95, "center"], "badge": ["OQIBAT", "coral"],
    "lines": [L("Milk *pasayadi*,", 78, "coral"), L("tish ildizi ochilib qoladi", 60)],
    "fx": [{"kind": "ring", "at": "gumline", "color": "coral", "r": 110}, {"kind": "bolts", "at": "gumline", "color": "orange", "r": 220, "delay": 1.4}]},
   {"img": "p2", "dur": 4.8, "view": [0.95, "center"], "badge": ["TO'G'RI", "teal"],
    "lines": [L("45° burchak, *yumshoq*", 68), L("aylanma harakat, 2 daqiqa", 58)],
    "fx": [{"kind": "sprite", "name": "brush", "at": "gumline", "path": "circle", "scale": 0.7, "rot": -20, "dy": 60, "delay": 0.4},
           {"kind": "sparkle", "at": "center", "delay": 2.6}]}]},
  {"type": "cta", "dur": 4.6, "img": "p2", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Kuniga *2 marta*,", 82), L("har biri 2 daqiqa", 64)]}],
 "instagram": "Tishni to'g'ri yuvasizmi? Ko'pchilik xato qiladi 🪥\n\n❌ Qattiq bosib, u yoq-bu yoqqa ishqalash milkni pasaytiradi — tish ildizi ochilib, sezgir bo'lib qoladi.\n✅ To'g'ri usul: yumshoq cho'tka, milkka 45° burchak, kichik aylanma harakatlar, kuniga 2 marta, 2 daqiqadan.\n\n💬 Cho'tkangizni har necha oyda almashtirasiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #tishyuvish",
})

# ---------------------------------------------------------------- 10 eroziya
EP.append({
 "id": "e10_gazli_ichimlik", "num": 10, "series": "Tish sirlari", "title": "Gazli ichimlik tishga nima qiladi",
 "assets": {"hero": {"build": "molar", "params": {}}, "soda": SPR["soda"], "lemon": SPR["lemon"],
            "e0": sec(), "e1": sec(enamel_scale=0.93, den_scale=0.84), "e2": sec(enamel_scale=0.88, den_scale=0.86)},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "hero", "pos": [540, 1170], "zoom": [1.05, 1.2], "center": "crown",
   "lines": [L("Gazli ichimlik", 84), L("tishga *nima qiladi*?", 78, "coral")]},
  {"type": "cause", "dur": 4.6, "img": "hero", "pos": [540, 1330], "scale": 1.0, "center": "crown", "falling": ["soda", "lemon", "soda"],
   "fall_scale": 0.42, "drops": "#9fe3ff", "badge": ["SABABI", "amber"],
   "lines": [L("Ichimlikdagi *kislota*", 72, "amber"), L("emalni yumshatadi", 66, None, 1.0)]},
  {"type": "stages", "steps": [
   {"img": "e0", "dur": 3.8, "view": [1.6, "crown"], "badge": ["SOG'LOM EMAL", "teal"],
    "lines": [L("Emal — tanadagi", 70), L("*eng qattiq* to'qima", 74)],
    "fx": [{"kind": "label", "at": "enamel", "text": "Emal", "color": "teal", "to": [330, 700], "delay": 0.9}]},
   {"img": "e1", "dur": 4.4, "view": [1.8, "crown"], "badge": ["EROZIYA", "amber"],
    "lines": [L("Har qultum kislota", 66), L("emalni *yupqalashtiradi*", 68, "amber")],
    "fx": [{"kind": "drops", "at": "top", "color": [150, 220, 255]}, {"kind": "ring", "at": "enamel", "color": "amber", "r": 90, "delay": 1.6}]},
   {"img": "e2", "dur": 4.4, "view": [1.8, "crown"], "badge": ["SEZUVCHANLIK", "orange"],
    "lines": [L("Emal yupqalashsa —", 68), L("*sovuq-issiqdan* sanchiq", 66, "orange")],
    "fx": [{"kind": "bolts", "at": "crown", "color": "orange", "r": 220}]},
   {"img": "e0", "dur": 4.4, "view": [1.6, "crown"], "badge": ["MASLAHAT", "teal"],
    "lines": [L("*Somincha* bilan iching,", 66), L("keyin suv bilan chayqang", 60)], "fx": [{"kind": "sparkle", "at": "crown"}]}]},
  {"type": "cta", "dur": 4.4, "img": "hero", "pos": [540, 900], "scale": 0.95, "center": "crown",
   "lines": [L("Ichgandan keyin *30 daqiqa*", 64), L("kutib, keyin tish yuving", 60)]}],
 "instagram": "Gazli ichimlik tishga nima qiladi? 🥤\n\nIchimlikdagi kislota emalni yumshatadi va asta-sekin yupqalashtiradi (eroziya). Emal yupqalashsa, tish sovuq-issiqdan sanchiydigan bo'ladi.\n\n✅ Somincha bilan iching\n✅ Keyin suv bilan chayqang\n✅ Darhol emas, 30 daqiqadan keyin tish yuving\n\n💬 Kuniga qancha gazli ichimlik ichasiz?\n📍 Olmaliq\n\n" + DISC + "\n\n" + TAGS + " #eroziya",
})

os.makedirs(OUT, exist_ok=True)
for e in EP:
    e.setdefault("tags", ["stomatologiya", "sogliq"])
    # fix L() with None accent
    for sc in e["scenes"]:
        for ln in sc.get("lines", []):
            if len(ln) > 2 and ln[2] is None: ln[2] = "teal"
        for st in sc.get("steps", []):
            for ln in st.get("lines", []):
                if len(ln) > 2 and ln[2] is None: ln[2] = "teal"
    json.dump(e, open(os.path.join(OUT, e["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(EP), "epizod yozildi")
