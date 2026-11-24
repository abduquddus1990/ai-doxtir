# Claude chat uchun prompt — @ai_olmaliq

Quyidagi butun matnni (shu qatordan pastini) Claude chatga nusxalab yuboring. Claude 10 ta ssenariyni JSON qilib beradi.
Javobdagi JSON'ni `.json` fayl qilib saqlang va GitHub'da **inbox/olmaliq/** papkasiga yuklang (Add file → Upload files).
50 ta kerak bo'lsa, shu suhbatda "yana 10 ta, oldingilarini takrorlama" deb 5 marta so'rang — har javobni alohida faylga saqlang.

---

Siz @ai_olmaliq — faqat Olmaliq shahri haqida 30-40 soniyalik 3D Reels: tarix, geografiya, kon-metallurgiya kombinati, kasblar, shahar hayoti, tabiat, kelajak rejalari. Auditoriya: Olmaliq aholisi. Til: o'zbek (lotin). FAKTLAR: faqat veb-qidiruvda ishonchli manbada (rasmiy saytlar, yirik OAV, ensiklopediya) tasdiqlanganini yozing; aniq raqamni faqat manbada ko'rsangiz yozing, aks holda raqamsiz yozing. Har tavsifda 'Manba: ...' qatori bo'lsin. Siyosat, mish-mish, shaxslar haqida salbiy gap, kombinat logotipi — yo'q.

Siz video dvigateli uchun epizod JSON fayllarini yozasiz. Dvigatel faqat quyidagilarni tushunadi — boshqa quruvchi, parametr, sahna turi ishlatmang.

@ai_olmaliq — 3D sahna quruvchilari (Blender bpy). engine/model3d.py ichidan ro'yxatga olinadi.

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
   "v0": {
    "build": "terrain",
    "params": {
     "trees": 30,
     "city": 0,
     "seed": 3
    }
   },
   "v1": {
    "build": "terrain",
    "params": {
     "trees": 18,
     "city": 0.35,
     "seed": 3
    }
   },
   "v2": {
    "build": "terrain",
    "params": {
     "trees": 8,
     "city": 0.9,
     "pin": true,
     "seed": 3
    }
   },
   "apple": {
    "build": "osprite",
    "params": {
     "kind": "apple"
    },
    "samples": 24
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.4,
    "img": "v0",
    "pos": [
     540,
     1180
    ],
    "zoom": [
     1.05,
     1.2
    ],
    "center": "orchard",
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
    "type": "cause",
    "dur": 4.4,
    "img": "v0",
    "pos": [
     540,
     1250
    ],
    "scale": 1.0,
    "center": "center",
    "falling": [
     "apple",
     "apple",
     "apple"
    ],
    "eat": false,
    "badge": [
     "QADIMDA",
     "teal"
    ],
    "lines": [
     [
      "Vodiyda *yovvoyi olma*",
      70,
      "teal"
     ],
     [
      "daraxtlari o'sgan",
      66,
      "teal"
     ]
    ]
   },
   {
    "type": "stages",
    "steps": [
     {
      "img": "v0",
      "dur": 4.0,
      "view": [
       1.5,
       "orchard"
      ],
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
      "fx": [
       {
        "kind": "ring",
        "at": "orchard",
        "color": "coral",
        "r": 150,
        "delay": 0.8
       }
      ]
     },
     {
      "img": "v1",
      "dur": 3.8,
      "view": [
       1.15,
       "city"
      ],
      "badge": [
       "QISHLOQDAN SHAHARGA",
       "teal"
      ],
      "lines": [
       [
        "Olmazor o'rnida",
        70,
        "teal"
       ],
       [
        "*uylar* paydo bo'ldi",
        70,
        "teal"
       ]
      ]
     },
     {
      "img": "v2",
      "dur": 4.4,
      "view": [
       1.15,
       "city"
      ],
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
      "fx": [
       {
        "kind": "sparkle",
        "at": "pin",
        "delay": 0.8
       }
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.6,
    "img": "v2",
    "pos": [
     540,
     980
    ],
    "scale": 0.9,
    "center": "center",
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
  "instagram": "Shahringiz nomi aslida nimani anglatadi? 🍎\n\nOlmaliq nomi vodiyda o'sgan yovvoyi olma daraxtlaridan olingan: \"olmasi ko'p joy\". Olmazor o'rnida qishloq, keyin shahar o'sdi. 1951-yil 10-iyulda Olmaliq shahar maqomini oldi.\n\n💬 Bobolaringizdan Olmaliqning eski olmazorlari haqida eshitganmisiz?\n📍 Olmaliq\n\nManba: Britannica, Wikipedia\n\n#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
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
   "m0": {
    "build": "terrain",
    "params": {
     "trees": 6,
     "city": 0.6,
     "pin": true,
     "seed": 5
    }
   },
   "m1": {
    "build": "terrain",
    "params": {
     "trees": 6,
     "city": 0.6,
     "seed": 5,
     "snow": true
    }
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.4,
    "img": "m0",
    "pos": [
     540,
     1160
    ],
    "zoom": [
     0.95,
     1.08
    ],
    "center": "center",
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
      "img": "m1",
      "dur": 4.4,
      "view": [
       1.25,
       "mountain"
      ],
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
      "fx": [
       {
        "kind": "label",
        "at": "mountain",
        "text": "Qurama",
        "color": "copper",
        "to": [
         330,
         760
        ],
        "side": "left",
        "delay": 1.0
       }
      ]
     },
     {
      "img": "m1",
      "dur": 4.4,
      "view": [
       1.35,
       "river"
      ],
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
      "fx": [
       {
        "kind": "label",
        "at": "river",
        "text": "Ohangaron",
        "color": "blue",
        "to": [
         820,
         860
        ],
        "side": "left",
        "delay": 1.0
       }
      ]
     },
     {
      "img": "m0",
      "dur": 4.4,
      "view": [
       1.3,
       "city"
      ],
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
      "fx": [
       {
        "kind": "ring",
        "at": "city",
        "color": "coral",
        "r": 120,
        "delay": 0.8
       }
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.6,
    "img": "m0",
    "pos": [
     540,
     980
    ],
    "scale": 0.9,
    "center": "center",
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
  "instagram": "Olmaliq nega aynan shu yerda qurilgan? ⛰\n\nShahar Qurama tog'larining shimoliy yonbag'rida, Ohangaron daryosining chap qirg'og'ida joylashgan. Tog'larda — ruda konlari, vodiyda — suv va hosildor yer.\n\n💬 Qurama tog'lariga chiqqanmisiz?\n📍 Olmaliq\n\nManba: Britannica, Wikipedia\n\n#olmaliq #almalyk #toshkentviloyati #olmaliqliklar #uzbekistan #3d #ai_olmaliq"
 }
]
```

Vazifa: 10 ta YANGI epizod yozing (series: "Olmaliq sirlari"). Faktlarni veb-qidiruvda tekshiring.
"id" va "num" ni yozmasangiz ham bo'ladi — dastur o'zi raqamlaydi.
Javobni bitta ```json blokida {"episodes": [ ... ]} ko'rinishida qaytaring.
