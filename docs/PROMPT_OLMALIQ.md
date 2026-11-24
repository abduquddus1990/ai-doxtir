# Claude chat uchun prompt — @ai_olmaliq

Quyidagi butun matnni (shu qatordan pastini) Claude chatga nusxalab yuboring. Claude 10 ta ssenariyni JSON qilib beradi.
Javobdagi JSON'ni `.json` fayl qilib saqlang va GitHub'da **inbox/olmaliq/** papkasiga yuklang (Add file → Upload files).
50 ta kerak bo'lsa, shu suhbatda "yana 10 ta, oldingilarini takrorlama" deb 5 marta so'rang — har javobni alohida faylga saqlang.

---

Siz @ai_olmaliq — faqat Olmaliq shahri haqida 30-40 soniyalik 3D Reels: tarix, geografiya, kon-metallurgiya kombinati, kasblar, shahar hayoti, tabiat, kelajak rejalari. Auditoriya: Olmaliq aholisi. Til: o'zbek (lotin). FAKTLAR: faqat veb-qidiruvda ishonchli manbada (rasmiy saytlar, yirik OAV, ensiklopediya) tasdiqlanganini yozing; aniq raqamni faqat manbada ko'rsangiz yozing, aks holda raqamsiz yozing. Har tavsifda 'Manba: ...' qatori bo'lsin. Siyosat, mish-mish, shaxslar haqida salbiy gap, kombinat logotipi — yo'q.

Siz video dvigateli uchun epizod JSON fayllarini yozasiz. Dvigatel faqat quyidagilarni tushunadi — boshqa quruvchi, parametr, sahna turi ishlatmang.

ASOSIY (fotoreal, imkon qadar shuni ishlating): @ai_olmaliq — HAQIQIY relyef va sun'iy yo'ldosh surati asosidagi 3D sahna (fotoreal).

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
geo sahnalarda: "zoom": [1.0, 1.1] (sekin yaqinlashish), "view": [1, "<anker>"] — fokus; geo asset hook/cta'da ham ishlatiladi.

QO'SHIMCHA (yaqin plan obyektlar): @ai_olmaliq — 3D sahna quruvchilari (Blender bpy). engine/model3d.py ichidan ro'yxatga olinadi.

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

Epizod JSON tuzilishi (namunalardagidek):
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
umumiy davomiylik 25-40 s. Har asset render ~1 daqiqa, shuning uchun bir xil assetni qayta ishlating.

Allaqachon mavjud mavzular (takrorlamang):
- Olmaliq nega "Olmaliq"?
- Shahar nega aynan shu yerda?
- Qalmoqqir karyeri ichiga tushamiz
- Bitta toshda 13 xil metall
- Toshdan mis simgacha
- Pufakchalar misni qanday ko'taradi
- Yer ostida konchining bir kuni
- Olmaliq: 1951 va bugun
- Olmaliq misi dunyo xaritasida
- Olmaliq 2028-yilda

Namuna epizodlar (format va uslub aynan shunday bo'lsin):
```json
[
 {
  "id": "o01_nomi",
  "num": 1,
  "series": "Olmaliq sirlari",
  "title": "Olmaliq nega \"Olmaliq\"?",
  "tags": [
   "olmaliq",
   "tarix"
  ],
  "assets": {
   "fly": {
    "build": "geo",
    "params": {
     "target": "ohangaron",
     "dist": 24,
     "tilt": 22,
     "heading": 330,
     "size": [
      1080,
      1920
     ],
     "fly": {
      "frames": 5,
      "dist_to": 15,
      "heading_to": 345,
      "tilt_to": 30
     }
    },
    "samples": 14
   },
   "vod": {
    "build": "geo",
    "params": {
     "target": "ohangaron",
     "dist": 7,
     "tilt": 38,
     "heading": 20,
     "size": [
      1080,
      1920
     ]
    },
    "samples": 14
   },
   "city": {
    "build": "geo",
    "params": {
     "target": "olmaliq",
     "dist": 9,
     "tilt": 45,
     "heading": 200,
     "size": [
      1080,
      1920
     ],
     "pins": [
      {
       "at": "olmaliq",
       "name": "city",
       "marker": true
      }
     ]
    },
    "samples": 14
   },
   "top": {
    "build": "geo",
    "params": {
     "target": "olmaliq",
     "dist": 6,
     "tilt": 70,
     "heading": 180,
     "size": [
      1080,
      1920
     ]
    },
    "samples": 14
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.6,
    "img": "fly",
    "zoom": [
     1.0,
     1.06
    ],
    "lines": [
     [
      "Shahringiz *nomi*",
      84,
      "teal"
     ],
     [
      "aslida nimani",
      70,
      "teal"
     ],
     [
      "*anglatadi*?",
      92,
      "copper"
     ]
    ]
   },
   {
    "type": "stages",
    "steps": [
     {
      "img": "vod",
      "dur": 4.4,
      "badge": [
       "QADIMDA",
       "teal"
      ],
      "lines": [
       [
        "Bu vodiyda *yovvoyi olma*",
        66,
        "teal"
       ],
       [
        "daraxtlari o'sgan",
        66,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "center"
      ]
     },
     {
      "img": "vod",
      "dur": 4.0,
      "badge": [
       "OLMA + LIQ",
       "copper"
      ],
      "lines": [
       [
        "*Olmaliq* —",
        80,
        "teal"
       ],
       [
        "olmasi ko'p joy",
        70,
        "teal"
       ]
      ],
      "zoom": [
       1.1,
       1.2
      ],
      "view": [
       1.0,
       "center"
      ]
     },
     {
      "img": "city",
      "dur": 4.2,
      "badge": [
       "BUGUN",
       "teal"
      ],
      "lines": [
       [
        "Olmazor o'rnida —",
        70,
        "teal"
       ],
       [
        "*shahar*",
        86,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "city"
      ]
     },
     {
      "img": "top",
      "dur": 4.4,
      "badge": [
       "1951-YIL 10-IYUL",
       "coral"
      ],
      "lines": [
       [
        "Olmaliq *shahar*",
        80,
        "teal"
       ],
       [
        "maqomini oldi",
        70,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "center"
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.6,
    "img": "city",
    "zoom": [
     1.1,
     1.18
    ],
    "lines": [
     [
      "Siz qaysi *mavze*dasiz?",
      74,
      "teal"
     ],
     [
      "Izohda yozing",
      60,
      "teal"
     ]
    ]
   }
  ],
  "instagram": "Shahringiz nomi aslida nimani anglatadi? 🍎\n\nOlmaliq nomi vodiyda o'sgan yovvoyi olma daraxtlaridan olingan: \"olmasi ko'p joy\". Olmazor o'rnida qishloq, keyin shahar o'sdi. 1951-yil 10-iyulda Olmaliq shahar maqomini oldi.\n\nVideodagi relyef va sun'iy yo'ldosh surati — haqiqiy.\n\n💬 Bobolaringizdan Olmaliqning eski olmazorlari haqida eshitganmisiz?\n📍 Olmaliq\n\nManba: Britannica, Wikipedia. Sun'iy yo'ldosh: Copernicus Sentinel-2 (2025), relyef: Copernicus DEM\n\n#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
 },
 {
  "id": "o02_joylashuv",
  "num": 2,
  "series": "Olmaliq sirlari",
  "title": "Shahar nega aynan shu yerda?",
  "tags": [
   "olmaliq",
   "geografiya"
  ],
  "assets": {
   "fly": {
    "build": "geo",
    "params": {
     "target": "olmaliq",
     "dist": 26,
     "tilt": 20,
     "heading": 10,
     "size": [
      1080,
      1920
     ],
     "fly": {
      "frames": 5,
      "dist_to": 17,
      "heading_to": 0,
      "tilt_to": 28
     },
     "pins": [
      {
       "at": "olmaliq",
       "name": "city",
       "marker": true
      }
     ]
    },
    "samples": 14
   },
   "qur": {
    "build": "geo",
    "params": {
     "target": "qurama",
     "dist": 14,
     "tilt": 22,
     "heading": 0,
     "size": [
      1080,
      1920
     ]
    },
    "samples": 14
   },
   "riv": {
    "build": "geo",
    "params": {
     "target": "ohangaron",
     "dist": 6,
     "tilt": 50,
     "heading": 190,
     "size": [
      1080,
      1920
     ]
    },
    "samples": 14
   },
   "mid": {
    "build": "geo",
    "params": {
     "target": "olmaliq",
     "dist": 11,
     "tilt": 38,
     "heading": 15,
     "size": [
      1080,
      1920
     ],
     "pins": [
      {
       "at": "olmaliq",
       "name": "city",
       "marker": true
      }
     ]
    },
    "samples": 14
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.6,
    "img": "fly",
    "lines": [
     [
      "Olmaliq nega",
      76,
      "teal"
     ],
     [
      "*aynan shu yerda*",
      86,
      "copper"
     ],
     [
      "qurilgan?",
      72,
      "teal"
     ]
    ]
   },
   {
    "type": "stages",
    "steps": [
     {
      "img": "qur",
      "dur": 4.4,
      "badge": [
       "JANUBDA",
       "teal"
      ],
      "lines": [
       [
        "*Qurama tog'lari*",
        80,
        "teal"
       ],
       [
        "shimoliy yonbag'ri",
        64,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "center"
      ]
     },
     {
      "img": "riv",
      "dur": 4.4,
      "badge": [
       "SUV",
       "blue"
      ],
      "lines": [
       [
        "*Ohangaron* daryosining",
        70,
        "teal"
       ],
       [
        "chap qirg'og'i",
        66,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "center"
      ]
     },
     {
      "img": "mid",
      "dur": 4.6,
      "badge": [
       "TOG' BAG'RIDA",
       "copper"
      ],
      "lines": [
       [
        "Tog'da — *ruda*,",
        76,
        "teal"
       ],
       [
        "vodiyda — *suv va yer*",
        66,
        "teal"
       ]
      ],
      "zoom": [
       1.0,
       1.1
      ],
      "view": [
       1.0,
       "city"
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.6,
    "img": "mid",
    "zoom": [
     1.1,
     1.18
    ],
    "lines": [
     [
      "Tog'lar, daryo va *ruda* —",
      66,
      "teal"
     ],
     [
      "shahar shu uchun shu yerda",
      56,
      "teal"
     ]
    ]
   }
  ],
  "instagram": "Olmaliq nega aynan shu yerda qurilgan? ⛰\n\nShahar Qurama tog'larining shimoliy yonbag'rida, Ohangaron daryosining chap qirg'og'ida joylashgan. Tog'larda — ruda konlari, vodiyda — suv va hosildor yer.\n\nVideodagi relyef va sun'iy yo'ldosh surati — haqiqiy.\n\n💬 Qurama tog'lariga chiqqanmisiz?\n📍 Olmaliq\n\nManba: Britannica, Wikipedia. Sun'iy yo'ldosh: Copernicus Sentinel-2 (2025), relyef: Copernicus DEM\n\n#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
 }
]
```

Vazifa: 10 ta YANGI epizod yozing (series: "Olmaliq sirlari"). Faktlarni veb-qidiruvda tekshiring.
"id" va "num" ni yozmasangiz ham bo'ladi — dastur o'zi raqamlaydi.
Javobni bitta ```json blokida {"episodes": [ ... ]} ko'rinishida qaytaring.
