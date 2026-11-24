"""@ai_olmaliq — 10 ta boshlang'ich epizod (channels/olmaliq/episodes/). Faktlar: docs/OLMALIQ_SSENARIYLAR.md (manbalari bilan).
Kadrlar: "geo" — Olmaliqning HAQIQIY relyefi (Copernicus DEM) + sun'iy yo'ldosh surati (Sentinel-2), fotoreal.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "channels", "olmaliq", "episodes")
SERIES = "Olmaliq sirlari"
TAGS = "#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
SRC_SAT = "Sun'iy yo'ldosh: Copernicus Sentinel-2 (2025), relyef: Copernicus DEM"
def L(text, size=72, acc="teal", delay=None):
    x = [text, size, acc]
    if delay is not None: x.append(delay)
    return x
def GEO(target, dist=12, tilt=35, heading=0, fly=None, pins=None, **kw):
    p = {"target": target, "dist": dist, "tilt": tilt, "heading": heading, "size": [1080, 1920]}
    if fly: p["fly"] = fly
    if pins: p["pins"] = pins
    p.update(kw)
    return {"build": "geo", "params": p, "samples": 14}
def FLY(dist_to, heading_to=None, tilt_to=None, frames=5):
    f = {"frames": frames, "dist_to": dist_to}
    if heading_to is not None: f["heading_to"] = heading_to
    if tilt_to is not None: f["tilt_to"] = tilt_to
    return f
PIN = lambda at, name: [{"at": at, "name": name, "marker": True}]
def SP(k): return {"build": "osprite", "params": {"kind": k}, "samples": 24}
def lab(at, text, to, color="teal", side="left", delay=1.0): return {"kind": "label", "at": at, "text": text, "color": color, "to": to, "side": side, "delay": delay}
def step(img, dur, badge, lines, focus=None, zoom=(1.0, 1.1), fx=None, view=None):
    s = {"img": img, "dur": dur, "badge": badge, "lines": lines, "zoom": list(zoom), "view": view or [1.0, focus or "center"]}
    if fx: s["fx"] = fx
    return s
def cap(hook, body, q, src, extra=""):
    return f"{hook}\n\n{body}\n\n💬 {q}\n📍 Olmaliq\n\nManba: {src}\n\n{TAGS}{extra}"

EP = []
# 1 — nomi
EP.append({"id": "o01_nomi", "num": 1, "series": SERIES, "title": "Olmaliq nega \"Olmaliq\"?", "tags": ["olmaliq", "tarix"],
 "assets": {"fly": GEO("ohangaron", 24, 22, 330, FLY(15, 345, 30)),
            "vod": GEO("ohangaron", 7, 38, 20),
            "city": GEO("olmaliq", 9, 45, 200, pins=PIN("olmaliq", "city")),
            "top": GEO("olmaliq", 6, 70, 180)},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "zoom": [1.0, 1.06], "lines": [L("Shahringiz *nomi*", 84), L("aslida nimani", 70), L("*anglatadi*?", 92, "copper")]},
  {"type": "stages", "steps": [
   step("vod", 4.4, ["QADIMDA", "teal"], [L("Bu vodiyda *yovvoyi olma*", 66), L("daraxtlari o'sgan", 66)]),
   step("vod", 4.0, ["OLMA + LIQ", "copper"], [L("*Olmaliq* —", 80), L("olmasi ko'p joy", 70)], zoom=(1.1, 1.2)),
   step("city", 4.2, ["BUGUN", "teal"], [L("Olmazor o'rnida —", 70), L("*shahar*", 86)], focus="city"),
   step("top", 4.4, ["1951-YIL 10-IYUL", "coral"], [L("Olmaliq *shahar*", 80), L("maqomini oldi", 70)])]},
  {"type": "cta", "dur": 4.6, "img": "city", "zoom": [1.1, 1.18], "lines": [L("Siz qaysi *mavze*dasiz?", 74), L("Izohda yozing", 60)]}],
 "instagram": cap("Shahringiz nomi aslida nimani anglatadi? 🍎",
  "Olmaliq nomi vodiyda o'sgan yovvoyi olma daraxtlaridan olingan: \"olmasi ko'p joy\". Olmazor o'rnida qishloq, keyin shahar o'sdi. 1951-yil 10-iyulda Olmaliq shahar maqomini oldi.\n\nVideodagi relyef va sun'iy yo'ldosh surati — haqiqiy.",
  "Bobolaringizdan Olmaliqning eski olmazorlari haqida eshitganmisiz?", "Britannica, Wikipedia. " + SRC_SAT)})
# 2 — joylashuv
EP.append({"id": "o02_joylashuv", "num": 2, "series": SERIES, "title": "Shahar nega aynan shu yerda?", "tags": ["olmaliq", "geografiya"],
 "assets": {"fly": GEO("olmaliq", 26, 20, 10, FLY(17, 0, 28), pins=PIN("olmaliq", "city")),
            "qur": GEO("qurama", 14, 22, 0), "riv": GEO("ohangaron", 6, 50, 190),
            "mid": GEO("olmaliq", 11, 38, 15, pins=PIN("olmaliq", "city"))},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Olmaliq nega", 76), L("*aynan shu yerda*", 86, "copper"), L("qurilgan?", 72)]},
  {"type": "stages", "steps": [
   step("qur", 4.4, ["JANUBDA", "teal"], [L("*Qurama tog'lari*", 80), L("shimoliy yonbag'ri", 64)]),
   step("riv", 4.4, ["SUV", "blue"], [L("*Ohangaron* daryosining", 70), L("chap qirg'og'i", 66)]),
   step("mid", 4.6, ["TOG' BAG'RIDA", "copper"], [L("Tog'da — *ruda*,", 76), L("vodiyda — *suv va yer*", 66)], focus="city")]},
  {"type": "cta", "dur": 4.6, "img": "mid", "zoom": [1.1, 1.18], "lines": [L("Tog'lar, daryo va *ruda* —", 66), L("shahar shu uchun shu yerda", 56)]}],
 "instagram": cap("Olmaliq nega aynan shu yerda qurilgan? ⛰",
  "Shahar Qurama tog'larining shimoliy yonbag'rida, Ohangaron daryosining chap qirg'og'ida joylashgan. Tog'larda — ruda konlari, vodiyda — suv va hosildor yer.\n\nVideodagi relyef va sun'iy yo'ldosh surati — haqiqiy.",
  "Qurama tog'lariga chiqqanmisiz?", "Britannica, Wikipedia. " + SRC_SAT)})
# 3 — karyer
EP.append({"id": "o03_karyer", "num": 3, "series": SERIES, "title": "Qalmoqqir karyeri ichiga tushamiz", "tags": ["olmaliq", "kon"],
 "assets": {"fly": GEO("karyer", 14, 30, 200, FLY(6, 170, 42), exag=1.3),
            "top": GEO("karyer", 5.5, 75, 180, exag=1.3), "near": GEO("karyer", 3.2, 38, 150, exag=1.3),
            "wide": GEO("karyer", 9, 30, 330, exag=1.3, pins=PIN("olmaliq", "city"))},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Olmaliq yonidagi", 70), L("*ulkan chuqurlik*", 88, "copper"), L("ichiga tushamiz", 70)]},
  {"type": "stages", "steps": [
   step("top", 4.2, ["QALMOQQIR", "copper"], [L("Ochiq usuldagi", 70), L("*mis* koni", 86, "copper")]),
   step("near", 4.4, ["POG'ONALAR", "teal"], [L("Karyer *zinapoya* kabi", 70), L("pog'onama-pog'ona chuqurlashadi", 54)], zoom=(1.0, 1.15)),
   step("near", 4.0, ["MIQYOS", "amber"], [L("Pog'onalar bo'ylab", 66), L("*ulkan yuk mashinalari*", 70, "amber"), L("yuradi", 66)], zoom=(1.15, 1.25)),
   step("wide", 4.4, ["ZANJIR BOSHI", "coral"], [L("Kombinat zanjirining", 66), L("*boshlang'ich nuqtasi*", 76, "coral")])]},
  {"type": "cta", "dur": 4.6, "img": "top", "zoom": [1.1, 1.2], "lines": [L("Keyingi qism: toshdan", 64), L("*mis sim*gacha", 80, "copper")]}],
 "instagram": cap("Olmaliq yonidagi ulkan chuqurlik ichiga tushamiz ⛏",
  "Qalmoqqir — ochiq usuldagi mis koni. Karyer pog'onama-pog'ona chuqurlashadi, pog'onalar bo'ylab ulkan yuk mashinalari yuradi. Bu yer — kombinat texnologik zanjirining boshlang'ich nuqtasi.\n\nVideodagi karyer relyefi va sun'iy yo'ldosh surati — haqiqiy.",
  "Karyerni yaqindan ko'rganmisiz?", "yuz.uz. " + SRC_SAT)})
# 4 — 13 metall
EP.append({"id": "o04_13_metall", "num": 4, "series": SERIES, "title": "Bitta toshda 13 xil metall", "tags": ["olmaliq", "kon"],
 "assets": {"fly": GEO("karyer", 10, 32, 210, FLY(5, 180, 45), exag=1.3),
            "r0": {"build": "ore", "params": {"split": 0}}, "r1": {"build": "ore", "params": {"split": 0.5}}, "r2": {"build": "ore", "params": {"split": 1}},
            "gold": SP("gold")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Shu karyer toshi", 76), L("oddiy *tosh*ga", 80), L("o'xshaydi, lekin...", 70)]},
  {"type": "stages", "steps": [
   {"img": "r0", "dur": 4.0, "view": [1.1, "center"], "badge": ["RUDA", "copper"], "lines": [L("Olmaliq rudasida", 72), L("*yaltiroq tomirlar* bor", 70, "copper")],
    "fx": [{"kind": "sparkle", "at": "center", "delay": 0.8}]},
   {"img": "r1", "dur": 4.0, "view": [1.0, "center"], "badge": ["AJRATAMIZ", "teal"], "lines": [L("Ichidan *metallar*", 76), L("chiqa boshlaydi", 70)]},
   {"img": "r2", "dur": 4.6, "view": [0.95, "center"], "badge": ["MIS · OLTIN · KUMUSH", "amber"], "lines": [L("Mis, oltin, kumush,", 66), L("*molibden, selen*...", 70, "amber")],
    "fx": [{"kind": "ring", "at": "m0", "color": "copper", "r": 60, "delay": 0.6}, {"kind": "ring", "at": "m1", "color": "amber", "r": 60, "delay": 1.0},
           {"kind": "ring", "at": "m2", "color": "grey", "r": 60, "delay": 1.4}]},
   {"img": "r2", "dur": 4.2, "view": [0.95, "center"], "badge": ["JAMI", "coral"], "lines": [L("*13 xil* element", 92, "coral")],
    "fx": [{"kind": "sparkle", "at": "m6", "delay": 0.6}]}]},
  {"type": "cta", "dur": 4.6, "img": "gold", "pos": [540, 950], "scale": 1.3,
   "lines": [L("Qaysi metall sizni", 70), L("*hayratlantirdi*?", 80, "amber")]}],
 "instagram": cap("Oddiy toshga o'xshaydi, lekin ichida 13 xil metall bor ✨",
  "Olmaliq kombinati rudasidan oltin, mis, kumush, molibden, selen kabi 13 turdagi element ajratib olinadi.",
  "Qaysi metall sizni hayratlantirdi?", "daryo.uz, president.uz", " #zargarlik")})
# 5 — mis sim
EP.append({"id": "o05_mis_sim", "num": 5, "series": SERIES, "title": "Toshdan mis simgacha", "tags": ["olmaliq", "kon"],
 "assets": {"fly": GEO("karyer", 9, 35, 160, FLY(5, 140, 45), exag=1.3), "zav": GEO("zavod", 5, 45, 200),
            "f0": {"build": "flotation", "params": {}}, "cath": SP("cathode"), "wire": SP("wire"), "phone": SP("phone")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Zaryadlagichingizdagi", 70), L("*mis* qayerdan", 84, "copper"), L("kelgan?", 72)]},
  {"type": "stages", "steps": [
   step("fly", 3.8, ["1 · KARYER", "copper"], [L("Qalmoqqirdan *ruda*", 76)], zoom=(1.1, 1.2)),
   step("zav", 3.8, ["2 · BOYITISH", "teal"], [L("Fabrikada ruda maydalanib,", 60), L("*konsentrat* olinadi", 70)]),
   {"img": "cath", "dur": 3.8, "view": [1.8, "center"], "badge": ["3 · MIS KATOD", "amber"], "lines": [L("Toza *mis plastina*", 76, "copper")]},
   {"img": "wire", "dur": 3.6, "view": [1.8, "center"], "badge": ["4 · SIM", "copper"], "lines": [L("Plastinadan —", 70), L("*mis sim*", 86, "copper")]},
   {"img": "phone", "dur": 3.8, "view": [1.7, "center"], "badge": ["5 · QO'LINGIZDA", "coral"], "lines": [L("Telefon *zaryadlagichi*", 72)]}]},
  {"type": "cta", "dur": 4.6, "img": "wire", "pos": [540, 950], "scale": 1.4,
   "lines": [L("Uyingizda nechta", 70), L("*mis sim* bor?", 80, "copper")]}],
 "instagram": cap("Telefon zaryadlagichingizdagi mis qayerdan kelgan? 🔌",
  "Yo'l shunday: Qalmoqqir karyeridan ruda → maydalash va boyitish (konsentrat) → toza mis katod plastinalari → mis sim → kabel va zaryadlagich.",
  "Uyingizdagi qaysi buyumda mis bor deb o'ylaysiz?", "yuz.uz, daryo.uz. " + SRC_SAT, " #elektronika")})
# 6 — flotatsiya
EP.append({"id": "o06_flotatsiya", "num": 6, "series": SERIES, "title": "Pufakchalar misni qanday ko'taradi", "tags": ["olmaliq", "kon", "talim"],
 "assets": {"fly": GEO("zavod", 12, 30, 220, FLY(5, 200, 45)),
            "f0": {"build": "flotation", "params": {"loaded": False, "bubbles": 30}}, "f1": {"build": "flotation", "params": {"loaded": True, "bubbles": 45}}},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Shu fabrikada oddiy", 70), L("*pufakcha*", 84), L("misni *ko'taradi*", 76, "copper")]},
  {"type": "stages", "steps": [
   {"img": "f0", "dur": 4.0, "view": [0.95, "tank"], "badge": ["FLOTATSIYA", "teal"], "lines": [L("Maydalangan ruda", 70), L("+ *suv* + reagent", 70, "blue")]},
   {"img": "f0", "dur": 4.0, "view": [1.1, "bottom"], "badge": ["HAVO", "blue"], "lines": [L("Pastdan *havo*", 76, "blue"), L("pufakchalari chiqadi", 66)]},
   {"img": "f1", "dur": 4.4, "view": [1.6, "bubble"], "badge": ["YOPISHADI", "copper"], "lines": [L("Mis zarralari", 70), L("pufakka *yopishadi*", 76, "copper")],
    "fx": [{"kind": "ring", "at": "bubble", "color": "copper", "r": 110, "delay": 0.8}]},
   {"img": "f1", "dur": 4.4, "view": [1.4, "froth"], "badge": ["KO'PIK", "amber"], "lines": [L("Ko'pik — *mis konsentrati*", 66, "amber")]},
   {"img": "f1", "dur": 4.2, "view": [0.95, "tank"], "badge": ["YANGI KORPUS", "coral"], "lines": [L("Yiliga *~917 ming t*", 80, "coral"), L("konsentrat quvvati", 62)]}]},
  {"type": "cta", "dur": 4.6, "img": "f1", "pos": [540, 980], "scale": 0.85, "center": "tank",
   "lines": [L("Kimyo darsida buni", 66), L("*o'rganganmisiz*?", 80)]}],
 "instagram": cap("Oddiy pufakcha misni qanday ko'taradi? 🫧",
  "Flotatsiya: maydalangan ruda suv va reagent bilan aralashtiriladi, pastdan havo yuboriladi. Mis zarralari pufakchalarga yopishib yuqoriga chiqadi va ko'pik — mis konsentrati yig'ib olinadi. Yangi korpus yiliga taxminan 917 ming tonna konsentrat quvvatiga ega.",
  "Kimyo darsida flotatsiyani o'rganganmisiz?", "kun.uz (2026-mart)", " #talim #kimyo")})
# 7 — konchi
EP.append({"id": "o07_konchi", "num": 7, "series": SERIES, "title": "Yer ostida konchining bir kuni", "tags": ["olmaliq", "kon", "kasb"],
 "assets": {"fly": GEO("karyer", 12, 28, 120, FLY(6, 100, 40), exag=1.3),
            "s0": {"build": "shaft", "params": {"cage": 0.05}}, "s1": {"build": "shaft", "params": {"cage": 0.55}}, "s2": {"build": "shaft", "params": {"cage": 1.0}},
            "helmet": SP("helmet")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("Yer ostida", 76), L("*bir kun*", 92, "copper"), L("qanday o'tadi?", 70)]},
  {"type": "stages", "steps": [
   {"img": "s0", "dur": 4.0, "view": [1.4, "headframe"], "badge": ["TONG", "amber"], "lines": [L("Smena *minora* oldida", 70), L("boshlanadi", 66)],
    "fx": [lab("headframe", "Minora", [330, 760], "copper")]},
   {"img": "s1", "dur": 4.0, "view": [1.0, "cage"], "badge": ["PASTGA", "teal"], "lines": [L("*Lift* konchilarni", 72), L("chuqurga tushiradi", 66)],
    "fx": [{"kind": "ring", "at": "cage", "color": "amber", "r": 90, "delay": 0.7}]},
   {"img": "s2", "dur": 4.4, "view": [1.0, "tunnel"], "badge": ["TUNNEL", "copper"], "lines": [L("Tunnelda — *ruda tomiri*", 66, "copper")],
    "fx": [{"kind": "sparkle", "at": "vein", "delay": 0.8}]},
   {"img": "helmet", "dur": 4.2, "view": [1.6, "center"], "badge": ["XAVFSIZLIK", "coral"], "lines": [L("Kaska, fonar, nazorat —", 62), L("*birinchi o'rinda*", 76, "coral")]}]},
  {"type": "cta", "dur": 4.6, "img": "fly", "zoom": [1.1, 1.2], "lines": [L("Oilangizda *konchi* bormi?", 66), L("Izohda yozing", 60)]}],
 "instagram": cap("Yer ostida konchining bir kuni qanday o'tadi? ⛑",
  "Smena minora oldida boshlanadi, lift konchilarni chuqurga tushiradi, tunnellarda ruda tomirlari qaziladi. Kaska, fonar va xavfsizlik nazorati — har doim birinchi o'rinda.",
  "Oilangizda konchi bormi? Unga rahmat ayting 👇", "Olmaliq KMK ochiq ma'lumotlari", " #kasb #konchi")})
# 8 — 1951 va bugun
EP.append({"id": "o08_1951_bugun", "num": 8, "series": SERIES, "title": "Olmaliq: 1951 va bugun", "tags": ["olmaliq", "tarix"],
 "assets": {"fly": GEO("olmaliq", 22, 25, 160, FLY(10, 190, 40), pins=PIN("olmaliq", "city")),
            "c1": GEO("olmaliq", 7, 55, 210), "c2": GEO("olmaliq", 4.5, 40, 240), "c3": GEO("olmaliq", 14, 30, 20, pins=PIN("olmaliq", "city"))},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("*1951*-yildan", 86, "copper"), L("bugungacha", 72), L("bir daqiqada", 70)]},
  {"type": "stages", "steps": [
   step("c1", 4.2, ["1951", "copper"], [L("10-iyul: Olmaliq", 70), L("*shahar* maqomini oldi", 70)]),
   step("c2", 4.2, ["O'SISH", "teal"], [L("Kombinat bilan", 70), L("shahar *kengaydi*", 74)], zoom=(1.0, 1.15)),
   step("c3", 4.6, ["BUGUN", "coral"], [L("Bugun — viloyatning", 66), L("*yirik sanoat shahri*", 72, "coral")], focus="city")]},
  {"type": "cta", "dur": 4.6, "img": "c3", "zoom": [1.1, 1.2], "lines": [L("Eski Olmaliq rasmi", 66), L("bormi? *Ulashing*", 72)]}],
 "instagram": cap("Olmaliq: 1951-yildan bugungacha bir daqiqada 🏙",
  "1951-yil 10-iyulda Olmaliq shahar maqomini oldi. Kombinat rivojlangani sari shahar ham kengaydi va bugun Toshkent viloyatining yirik sanoat shaharlaridan biri.\n\nVideodagi shahar — 2025-yilgi haqiqiy sun'iy yo'ldosh surati.",
  "Eski Olmaliq suratlari bormi? Izohda ulashing", "Britannica, Wikipedia. " + SRC_SAT, " #tarix")})
# 9 — dunyo
EP.append({"id": "o09_dunyo", "num": 9, "series": SERIES, "title": "Olmaliq misi dunyo xaritasida", "tags": ["olmaliq", "kon"],
 "assets": {"g0": {"build": "globe", "params": {"arcs": 0}}, "g1": {"build": "globe", "params": {"arcs": 4}},
            "land": GEO("olmaliq", 16, 32, 200, FLY(8, 200, 45), pins=PIN("olmaliq", "city"))},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "g0", "pos": [540, 1170], "zoom": [0.95, 1.1], "center": "olmaliq",
   "lines": [L("Dunyo xaritasida", 74), L("*Olmaliq* qayerda?", 84, "copper")]},
  {"type": "stages", "steps": [
   {"img": "g0", "dur": 3.6, "view": [1.6, "olmaliq"], "badge": ["MARKAZIY OSIYO", "teal"], "lines": [L("Mana shu *qizil nuqta*", 72, "coral")],
    "fx": [{"kind": "ring", "at": "olmaliq", "color": "coral", "r": 60, "delay": 0.6}]},
   step("land", 4.0, ["YAQINROQ", "copper"], [L("Mana — *Olmaliq*", 80, "copper")], focus="city"),
   {"img": "g1", "dur": 4.4, "view": [1.0, "center"], "badge": ["MIS YO'LLARI", "copper"], "lines": [L("Olmaliq misi", 72), L("*dunyo bo'ylab* ketadi", 70, "copper")]},
   {"img": "g1", "dur": 4.6, "view": [1.0, "center"], "badge": ["TOP-30", "coral"], "lines": [L("Mis bo'yicha dunyodagi", 64), L("*30 eng yirik* korxona", 72, "coral"), L("safida", 64)]}]},
  {"type": "cta", "dur": 4.6, "img": "land", "zoom": [1.1, 1.2], "lines": [L("Olmaliq bilan", 70), L("*faxrlanasizmi*?", 82, "copper")]}],
 "instagram": cap("Dunyo xaritasida Olmaliq qayerda? 🌍",
  "Olmaliq kon-metallurgiya kombinati mis ishlab chiqarish bo'yicha dunyodagi 30 ta eng yirik korxona safida. Olmaliq misi dunyo bozorlariga yo'l oladi.",
  "Olmaliq bilan faxrlanasizmi?", "yuz.uz. Globus: NASA Blue Marble. " + SRC_SAT, " #logistika")})
# 10 — 2028
EP.append({"id": "o10_2028", "num": 10, "series": SERIES, "title": "Olmaliq 2028-yilda", "tags": ["olmaliq", "kelajak"],
 "assets": {"fly": GEO("olmaliq", 20, 24, 200, FLY(12, 215, 34), pins=PIN("olmaliq", "city")),
            "kar": GEO("karyer", 6, 45, 170, exag=1.3), "cath": SP("cathode"), "gold": SP("gold"), "silver": SP("silver")},
 "scenes": [
  {"type": "hook", "dur": 3.6, "img": "fly", "lines": [L("*2028*-yilda", 92, "copper"), L("Olmaliq qanday", 70), L("bo'ladi?", 72)]},
  {"type": "stages", "steps": [
   step("fly", 3.8, ["BUGUN", "teal"], [L("Bugungi shahar", 72)], zoom=(1.1, 1.2), focus="city"),
   step("kar", 4.2, ["REJA", "copper"], [L("Yangi quvvatlar", 70), L("*rejalashtirilgan*", 78, "copper")]),
   {"img": "cath", "dur": 3.8, "view": [1.7, "center"], "badge": ["MIS", "copper"], "lines": [L("Yiliga *400 ming t*", 80, "copper")]},
   {"img": "gold", "dur": 3.8, "view": [1.7, "center"], "badge": ["OLTIN", "amber"], "lines": [L("Yiliga *50 t*", 88, "amber")]},
   {"img": "silver", "dur": 3.8, "view": [1.7, "center"], "badge": ["KUMUSH", "grey"], "lines": [L("Yiliga *270 t*", 88, "grey")]}]},
  {"type": "cta", "dur": 4.6, "img": "fly", "zoom": [1.15, 1.25], "lines": [L("2028-yilda siz", 70), L("*qayerda* bo'lasiz?", 80, "copper")]}],
 "instagram": cap("2028-yilda Olmaliq qanday bo'ladi? 🚀",
  "Rejaga ko'ra, 2028-yilga borib kombinatning yillik quvvati 400 ming tonna mis, 50 tonna oltin va 270 tonna kumushga yetkazilishi rejalashtirilgan.",
  "2028-yilda o'zingizni qayerda ko'rasiz?", "president.uz. " + SRC_SAT, " #kelajak")})

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for e in EP:
        json.dump(e, open(os.path.join(OUT, e["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(EP), "epizod yozildi:", OUT)
