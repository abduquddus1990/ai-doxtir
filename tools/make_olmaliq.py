"""@ai_olmaliq — 10 ta boshlang'ich epizod (channels/olmaliq/episodes/). Faktlar: docs/OLMALIQ_SSENARIYLAR.md (manbalari bilan)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "channels", "olmaliq", "episodes")
SERIES = "Olmaliq sirlari"
TAGS = "#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
def L(text, size=72, acc="teal", delay=None):
    x = [text, size, acc]
    if delay is not None: x.append(delay)
    return x
def T(**p): return {"build": "terrain", "params": p}
def SP(k): return {"build": "osprite", "params": {"kind": k}, "samples": 24}
def lab(at, text, to, color="teal", side="left", delay=1.0): return {"kind": "label", "at": at, "text": text, "color": color, "to": to, "side": side, "delay": delay}
def cap(hook, body, q, src, extra=""):
    return f"{hook}\n\n{body}\n\n💬 {q}\n📍 Olmaliq\n\nManba: {src}\n\n{TAGS}{extra}"

EP = []
# 1
EP.append({"id": "o01_nomi", "num": 1, "series": SERIES, "title": "Olmaliq nega \"Olmaliq\"?", "tags": ["olmaliq", "tarix"],
 "assets": {"v0": T(trees=30, city=0, seed=3), "v1": T(trees=18, city=0.35, seed=3), "v2": T(trees=8, city=0.9, pin=True, seed=3), "apple": SP("apple")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "v0", "pos": [540, 1180], "zoom": [1.05, 1.2], "center": "orchard",
   "lines": [L("Shahringiz *nomi*", 84), L("aslida nimani", 70), L("*anglatadi*?", 92, "copper")]},
  {"type": "cause", "dur": 4.4, "img": "v0", "pos": [540, 1250], "scale": 1.0, "center": "center", "falling": ["apple", "apple", "apple"], "eat": False,
   "badge": ["QADIMDA", "teal"], "lines": [L("Vodiyda *yovvoyi olma*", 70), L("daraxtlari o'sgan", 66)]},
  {"type": "stages", "steps": [
   {"img": "v0", "dur": 4.0, "view": [1.5, "orchard"], "badge": ["OLMA + LIQ", "copper"], "lines": [L("*Olmaliq* —", 80), L("olmasi ko'p joy", 70)],
    "fx": [{"kind": "ring", "at": "orchard", "color": "coral", "r": 150, "delay": 0.8}]},
   {"img": "v1", "dur": 3.8, "view": [1.15, "city"], "badge": ["QISHLOQDAN SHAHARGA", "teal"], "lines": [L("Olmazor o'rnida", 70), L("*uylar* paydo bo'ldi", 70)]},
   {"img": "v2", "dur": 4.4, "view": [1.15, "city"], "badge": ["1951-YIL 10-IYUL", "coral"], "lines": [L("Olmaliq *shahar*", 80), L("maqomini oldi", 70)],
    "fx": [{"kind": "sparkle", "at": "pin", "delay": 0.8}]}]},
  {"type": "cta", "dur": 4.6, "img": "v2", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Siz qaysi *mavze*dasiz?", 74), L("Izohda yozing", 60)]}],
 "instagram": cap("Shahringiz nomi aslida nimani anglatadi? 🍎",
  "Olmaliq nomi vodiyda o'sgan yovvoyi olma daraxtlaridan olingan: \"olmasi ko'p joy\". Olmazor o'rnida qishloq, keyin shahar o'sdi. 1951-yil 10-iyulda Olmaliq shahar maqomini oldi.",
  "Bobolaringizdan Olmaliqning eski olmazorlari haqida eshitganmisiz?", "Britannica, Wikipedia")})
# 2
EP.append({"id": "o02_joylashuv", "num": 2, "series": SERIES, "title": "Shahar nega aynan shu yerda?", "tags": ["olmaliq", "geografiya"],
 "assets": {"m0": T(trees=6, city=0.6, pin=True, seed=5), "m1": T(trees=6, city=0.6, seed=5, snow=True)},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "m0", "pos": [540, 1160], "zoom": [0.95, 1.08], "center": "center",
   "lines": [L("Olmaliq nega", 76), L("*aynan shu yerda*", 86, "copper"), L("qurilgan?", 72)]},
  {"type": "stages", "steps": [
   {"img": "m1", "dur": 4.4, "view": [1.25, "mountain"], "badge": ["JANUBDA", "teal"], "lines": [L("*Qurama tog'lari*", 80), L("shimoliy yonbag'ri", 64)],
    "fx": [lab("mountain", "Qurama", [330, 760], "copper")]},
   {"img": "m1", "dur": 4.4, "view": [1.35, "river"], "badge": ["SUV", "blue"], "lines": [L("*Ohangaron* daryosining", 70), L("chap qirg'og'i", 66)],
    "fx": [lab("river", "Ohangaron", [820, 860], "blue", "left")]},
   {"img": "m0", "dur": 4.4, "view": [1.3, "city"], "badge": ["TOG' BAG'RIDA", "copper"], "lines": [L("Tog'da — *ruda*,", 76), L("vodiyda — *suv va yer*", 66)],
    "fx": [{"kind": "ring", "at": "city", "color": "coral", "r": 120, "delay": 0.8}]}]},
  {"type": "cta", "dur": 4.6, "img": "m0", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Tog'lar, daryo va *ruda* —", 66), L("shahar shu uchun shu yerda", 56)]}],
 "instagram": cap("Olmaliq nega aynan shu yerda qurilgan? ⛰",
  "Shahar Qurama tog'larining shimoliy yonbag'rida, Ohangaron daryosining chap qirg'og'ida joylashgan. Tog'larda — ruda konlari, vodiyda — suv va hosildor yer.",
  "Qurama tog'lariga chiqqanmisiz?", "Britannica, Wikipedia")})
# 3
EP.append({"id": "o03_karyer", "num": 3, "series": SERIES, "title": "Qalmoqqir karyeri ichiga tushamiz", "tags": ["olmaliq", "kon"],
 "assets": {"q0": {"build": "quarry", "params": {"trucks": 3}}, "q1": {"build": "quarry", "params": {"trucks": 6}}, "truck": SP("truck")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "q0", "pos": [540, 1170], "zoom": [0.95, 1.12], "center": "center",
   "lines": [L("Olmaliq yonidagi", 70), L("*ulkan chuqurlik*", 88, "copper"), L("ichiga tushamiz", 70)]},
  {"type": "stages", "steps": [
   {"img": "q0", "dur": 4.2, "view": [1.05, "center"], "badge": ["QALMOQQIR", "copper"], "lines": [L("Ochiq usuldagi", 70), L("*mis* koni", 86, "copper")]},
   {"img": "q0", "dur": 4.2, "view": [1.5, "bench"], "badge": ["POG'ONALAR", "teal"], "lines": [L("Karyer *zinapoya* kabi", 70), L("pog'onama-pog'ona chuqurlashadi", 54)],
    "fx": [{"kind": "ring", "at": "bench", "color": "amber", "r": 110, "delay": 0.8}]},
   {"img": "q1", "dur": 4.2, "view": [1.15, "truck"], "badge": ["MIQYOS", "amber"], "lines": [L("Bu nuqtalar —", 70), L("*ulkan yuk mashinalari*", 70, "amber")],
    "fx": [{"kind": "ring", "at": "truck", "color": "coral", "r": 70, "delay": 0.6}]},
   {"img": "q1", "dur": 4.4, "view": [1.2, "bottom"], "badge": ["ZANJIR BOSHI", "coral"], "lines": [L("Kombinat zanjirining", 66), L("*boshlang'ich nuqtasi*", 76, "coral")],
    "fx": [{"kind": "arrow", "from": "rim", "at": "bottom", "color": "coral"}]}]},
  {"type": "cta", "dur": 4.6, "img": "q1", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Keyingi qism: toshdan", 64), L("*mis sim*gacha", 80, "copper")]}],
 "instagram": cap("Olmaliq yonidagi ulkan chuqurlik ichiga tushamiz ⛏",
  "Qalmoqqir — ochiq usuldagi mis koni. Karyer pog'onama-pog'ona chuqurlashadi, pog'onalardagi kichik nuqtalar aslida ulkan yuk mashinalari. Bu yer — kombinat texnologik zanjirining boshlang'ich nuqtasi.",
  "Karyerni yaqindan ko'rganmisiz?", "yuz.uz")})
# 4
EP.append({"id": "o04_13_metall", "num": 4, "series": SERIES, "title": "Bitta toshda 13 xil metall", "tags": ["olmaliq", "kon"],
 "assets": {"r0": {"build": "ore", "params": {"split": 0}}, "r1": {"build": "ore", "params": {"split": 0.5}}, "r2": {"build": "ore", "params": {"split": 1}},
            "gold": SP("gold")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "r0", "pos": [540, 1170], "zoom": [1.0, 1.15], "center": "center",
   "lines": [L("Oddiy *tosh*ga", 80), L("o'xshaydi, lekin...", 70)]},
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
# 5
EP.append({"id": "o05_mis_sim", "num": 5, "series": SERIES, "title": "Toshdan mis simgacha", "tags": ["olmaliq", "kon"],
 "assets": {"r0": {"build": "ore", "params": {"split": 0}}, "f0": {"build": "flotation", "params": {}}, "cath": SP("cathode"), "wire": SP("wire"), "phone": SP("phone")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "phone", "pos": [540, 1170], "zoom": [1.3, 1.45], "center": "center",
   "lines": [L("Zaryadlagichingizdagi", 70), L("*mis* qayerdan", 84, "copper"), L("kelgan?", 72)]},
  {"type": "stages", "steps": [
   {"img": "r0", "dur": 3.6, "view": [1.0, "center"], "badge": ["1 · RUDA", "copper"], "lines": [L("Karyerdan *ruda*", 76)]},
   {"img": "f0", "dur": 3.8, "view": [0.95, "tank"], "badge": ["2 · BOYITISH", "teal"], "lines": [L("Ruda maydalanib,", 66), L("*konsentrat* olinadi", 70)]},
   {"img": "cath", "dur": 3.8, "view": [1.8, "center"], "badge": ["3 · MIS KATOD", "amber"], "lines": [L("Toza *mis plastina*", 76, "copper")]},
   {"img": "wire", "dur": 3.6, "view": [1.8, "center"], "badge": ["4 · SIM", "copper"], "lines": [L("Plastinadan —", 70), L("*mis sim*", 86, "copper")]},
   {"img": "phone", "dur": 3.8, "view": [1.7, "center"], "badge": ["5 · QO'LINGIZDA", "coral"], "lines": [L("Telefon *zaryadlagichi*", 72)]}]},
  {"type": "cta", "dur": 4.6, "img": "wire", "pos": [540, 950], "scale": 1.4,
   "lines": [L("Uyingizda nechta", 70), L("*mis sim* bor?", 80, "copper")]}],
 "instagram": cap("Telefon zaryadlagichingizdagi mis qayerdan kelgan? 🔌",
  "Yo'l shunday: karyerdan ruda → maydalash va boyitish (konsentrat) → toza mis katod plastinalari → mis sim → kabel va zaryadlagich.",
  "Uyingizdagi qaysi buyumda mis bor deb o'ylaysiz?", "yuz.uz, daryo.uz", " #elektronika")})
# 6
EP.append({"id": "o06_flotatsiya", "num": 6, "series": SERIES, "title": "Pufakchalar misni qanday ko'taradi", "tags": ["olmaliq", "kon", "talim"],
 "assets": {"f0": {"build": "flotation", "params": {"loaded": False, "bubbles": 30}}, "f1": {"build": "flotation", "params": {"loaded": True, "bubbles": 45}}},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "f1", "pos": [540, 1170], "zoom": [1.0, 1.15], "center": "bubble",
   "lines": [L("Oddiy *pufakcha*", 80), L("misni yuqoriga", 70), L("*ko'taradi*", 88, "copper")]},
  {"type": "stages", "steps": [
   {"img": "f0", "dur": 4.0, "view": [0.95, "tank"], "badge": ["FLOTATSIYA", "teal"], "lines": [L("Maydalangan ruda", 70), L("+ *suv* + reagent", 70, "blue")]},
   {"img": "f0", "dur": 4.0, "view": [1.1, "bottom"], "badge": ["HAVO", "blue"], "lines": [L("Pastdan *havo*", 76, "blue"), L("pufakchalari chiqadi", 66)]},
   {"img": "f1", "dur": 4.4, "view": [1.9, "bubble"], "badge": ["YOPISHADI", "copper"], "lines": [L("Mis zarralari", 70), L("pufakka *yopishadi*", 76, "copper")],
    "fx": [{"kind": "ring", "at": "bubble", "color": "copper", "r": 110, "delay": 0.8}]},
   {"img": "f1", "dur": 4.4, "view": [1.4, "froth"], "badge": ["KO'PIK", "amber"], "lines": [L("Ko'pik — *mis konsentrati*", 66, "amber")]},
   {"img": "f1", "dur": 4.2, "view": [0.95, "tank"], "badge": ["YANGI KORPUS", "coral"], "lines": [L("Yiliga *~917 ming t*", 80, "coral"), L("konsentrat quvvati", 62)]}]},
  {"type": "cta", "dur": 4.6, "img": "f1", "pos": [540, 980], "scale": 0.85, "center": "tank",
   "lines": [L("Kimyo darsida buni", 66), L("*o'rganganmisiz*?", 80)]}],
 "instagram": cap("Oddiy pufakcha misni qanday ko'taradi? 🫧",
  "Flotatsiya: maydalangan ruda suv va reagent bilan aralashtiriladi, pastdan havo yuboriladi. Mis zarralari pufakchalarga yopishib yuqoriga chiqadi va ko'pik — mis konsentrati yig'ib olinadi. Yangi korpus yiliga taxminan 917 ming tonna konsentrat quvvatiga ega.",
  "Kimyo darsida flotatsiyani o'rganganmisiz?", "kun.uz (2026-mart)", " #talim #kimyo")})
# 7
EP.append({"id": "o07_konchi", "num": 7, "series": SERIES, "title": "Yer ostida konchining bir kuni", "tags": ["olmaliq", "kon", "kasb"],
 "assets": {"s0": {"build": "shaft", "params": {"cage": 0.05}}, "s1": {"build": "shaft", "params": {"cage": 0.55}}, "s2": {"build": "shaft", "params": {"cage": 1.0}},
            "helmet": SP("helmet")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "s0", "pos": [540, 1100], "zoom": [0.85, 0.95], "center": "surface",
   "lines": [L("Yer ostida", 76), L("*bir kun*", 92, "copper"), L("qanday o'tadi?", 70)]},
  {"type": "stages", "steps": [
   {"img": "s0", "dur": 4.0, "view": [1.4, "headframe"], "badge": ["TONG", "amber"], "lines": [L("Smena *minora* oldida", 70), L("boshlanadi", 66)],
    "fx": [lab("headframe", "Minora", [330, 760], "copper")]},
   {"img": "s1", "dur": 4.0, "view": [1.0, "cage"], "badge": ["PASTGA", "teal"], "lines": [L("*Lift* konchilarni", 72), L("chuqurga tushiradi", 66)],
    "fx": [{"kind": "ring", "at": "cage", "color": "amber", "r": 90, "delay": 0.7}]},
   {"img": "s2", "dur": 4.4, "view": [1.0, "tunnel"], "badge": ["TUNNEL", "copper"], "lines": [L("Tunnelda — *ruda tomiri*", 66, "copper")],
    "fx": [{"kind": "sparkle", "at": "vein", "delay": 0.8}]},
   {"img": "helmet", "dur": 4.2, "view": [1.6, "center"], "badge": ["XAVFSIZLIK", "coral"], "lines": [L("Kaska, fonar, nazorat —", 62), L("*birinchi o'rinda*", 76, "coral")]}]},
  {"type": "cta", "dur": 4.6, "img": "helmet", "pos": [540, 950], "scale": 1.2,
   "lines": [L("Oilangizda *konchi* bormi?", 66), L("Izohda yozing", 60)]}],
 "instagram": cap("Yer ostida konchining bir kuni qanday o'tadi? ⛑",
  "Smena minora oldida boshlanadi, lift konchilarni chuqurga tushiradi, tunnellarda ruda tomirlari qaziladi. Kaska, fonar va xavfsizlik nazorati — har doim birinchi o'rinda.",
  "Oilangizda konchi bormi? Unga rahmat ayting 👇", "Olmaliq KMK ochiq ma'lumotlari", " #kasb #konchi")})
# 8
EP.append({"id": "o08_1951_bugun", "num": 8, "series": SERIES, "title": "Olmaliq: 1951 va bugun", "tags": ["olmaliq", "tarix"],
 "assets": {"c0": T(trees=14, city=0.12, seed=8), "c1": T(trees=8, city=0.5, seed=8), "c2": T(trees=4, city=1.0, pin=True, seed=8)},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "c0", "pos": [540, 1160], "zoom": [1.0, 1.1], "center": "city",
   "lines": [L("*1951*-yildan", 86, "copper"), L("bugungacha", 72), L("bir daqiqada", 70)]},
  {"type": "stages", "steps": [
   {"img": "c0", "dur": 4.2, "view": [1.35, "city"], "badge": ["1951", "copper"], "lines": [L("10-iyul: Olmaliq", 70), L("*shahar* maqomini oldi", 70)]},
   {"img": "c1", "dur": 4.2, "view": [1.2, "city"], "badge": ["O'SISH", "teal"], "lines": [L("Kombinat bilan", 70), L("shahar *kengaydi*", 74)]},
   {"img": "c2", "dur": 4.6, "view": [1.05, "city"], "badge": ["BUGUN", "coral"], "lines": [L("Bugun — viloyatning", 66), L("*yirik sanoat shahri*", 72, "coral")],
    "fx": [{"kind": "sparkle", "at": "pin", "delay": 0.8}]}]},
  {"type": "cta", "dur": 4.6, "img": "c2", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("Eski Olmaliq rasmi", 66), L("bormi? *Ulashing*", 72)]}],
 "instagram": cap("Olmaliq: 1951-yildan bugungacha bir daqiqada 🏙",
  "1951-yil 10-iyulda Olmaliq shahar maqomini oldi. Kombinat rivojlangani sari shahar ham kengaydi va bugun Toshkent viloyatining yirik sanoat shaharlaridan biri.",
  "Eski Olmaliq suratlari bormi? Izohda ulashing", "Britannica, Wikipedia", " #tarix")})
# 9
EP.append({"id": "o09_dunyo", "num": 9, "series": SERIES, "title": "Olmaliq misi dunyo xaritasida", "tags": ["olmaliq", "kon"],
 "assets": {"g0": {"build": "globe", "params": {"arcs": 0}}, "g1": {"build": "globe", "params": {"arcs": 4}}, "cath": SP("cathode")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "g0", "pos": [540, 1170], "zoom": [0.95, 1.1], "center": "olmaliq",
   "lines": [L("Dunyo xaritasida", 74), L("*Olmaliq* qayerda?", 84, "copper")]},
  {"type": "stages", "steps": [
   {"img": "g0", "dur": 4.0, "view": [1.6, "olmaliq"], "badge": ["MARKAZIY OSIYO", "teal"], "lines": [L("Mana shu *qizil nuqta*", 72, "coral")],
    "fx": [{"kind": "ring", "at": "olmaliq", "color": "coral", "r": 60, "delay": 0.6}]},
   {"img": "g1", "dur": 4.4, "view": [1.0, "center"], "badge": ["MIS YO'LLARI", "copper"], "lines": [L("Olmaliq misi", 72), L("*dunyo bo'ylab* ketadi", 70, "copper")]},
   {"img": "g1", "dur": 4.6, "view": [1.0, "center"], "badge": ["TOP-30", "coral"], "lines": [L("Mis bo'yicha dunyodagi", 64), L("*30 eng yirik* korxona", 72, "coral"), L("safida", 64)]}]},
  {"type": "cta", "dur": 4.6, "img": "cath", "pos": [540, 950], "scale": 1.3,
   "lines": [L("Olmaliq bilan", 70), L("*faxrlanasizmi*?", 82, "copper")]}],
 "instagram": cap("Dunyo xaritasida Olmaliq qayerda? 🌍",
  "Olmaliq kon-metallurgiya kombinati mis ishlab chiqarish bo'yicha dunyodagi 30 ta eng yirik korxona safida. Olmaliq misi dunyo bozorlariga yo'l oladi.",
  "Olmaliq bilan faxrlanasizmi?", "yuz.uz", " #logistika")})
# 10
EP.append({"id": "o10_2028", "num": 10, "series": SERIES, "title": "Olmaliq 2028-yilda", "tags": ["olmaliq", "kelajak"],
 "assets": {"k0": T(trees=6, city=0.85, seed=11), "k1": T(trees=10, city=1.0, future=True, pin=True, seed=11), "cath": SP("cathode"), "gold": SP("gold"), "silver": SP("silver")},
 "scenes": [
  {"type": "hook", "dur": 3.4, "img": "k1", "pos": [540, 1160], "zoom": [0.95, 1.1], "center": "city",
   "lines": [L("*2028*-yilda", 92, "copper"), L("Olmaliq qanday", 70), L("bo'ladi?", 72)]},
  {"type": "stages", "steps": [
   {"img": "k0", "dur": 3.8, "view": [1.15, "city"], "badge": ["BUGUN", "teal"], "lines": [L("Bugungi shahar", 72)]},
   {"img": "k1", "dur": 4.2, "view": [1.15, "city"], "badge": ["REJA", "copper"], "lines": [L("Yangi quvvatlar", 70), L("*rejalashtirilgan*", 78, "copper")]},
   {"img": "cath", "dur": 3.8, "view": [1.7, "center"], "badge": ["MIS", "copper"], "lines": [L("Yiliga *400 ming t*", 80, "copper")]},
   {"img": "gold", "dur": 3.8, "view": [1.7, "center"], "badge": ["OLTIN", "amber"], "lines": [L("Yiliga *50 t*", 88, "amber")]},
   {"img": "silver", "dur": 3.8, "view": [1.7, "center"], "badge": ["KUMUSH", "grey"], "lines": [L("Yiliga *270 t*", 88, "grey")]}]},
  {"type": "cta", "dur": 4.6, "img": "k1", "pos": [540, 980], "scale": 0.9, "center": "center",
   "lines": [L("2028-yilda siz", 70), L("*qayerda* bo'lasiz?", 80, "copper")]}],
 "instagram": cap("2028-yilda Olmaliq qanday bo'ladi? 🚀",
  "Rejaga ko'ra, 2028-yilga borib kombinatning yillik quvvati 400 ming tonna mis, 50 tonna oltin va 270 tonna kumushga yetkazilishi rejalashtirilgan.",
  "2028-yilda o'zingizni qayerda ko'rasiz?", "president.uz", " #kelajak")})

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for e in EP:
        json.dump(e, open(os.path.join(OUT, e["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(EP), "epizod yozildi:", OUT)
