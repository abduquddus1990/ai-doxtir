# Claude chat uchun prompt — @ai_doxtir

Quyidagi butun matnni (shu qatordan pastini) Claude chatga nusxalab yuboring. Claude 10 ta ssenariyni JSON qilib beradi.
Javobdagi JSON'ni `.json` fayl qilib saqlang va GitHub'da **inbox/doxtir/** papkasiga yuklang (Add file → Upload files).
50 ta kerak bo'lsa, shu suhbatda "yana 10 ta, oldingilarini takrorlama" deb 5 marta so'rang — har javobni alohida faylga saqlang.

---

Siz @ai_doxtir — stomatologiya (tish salomatligi) haqida 30-40 soniyalik 3D Reels. Auditoriya: Olmaliq shahri aholisi (Toshkent viloyati). Til: o'zbek (lotin). Tibbiy ma'lumotlar zamonaviy dalillarga asoslangan, qo'rqitmasdan, amaliy maslahat bilan. Hech qachon dori nomi/dozasi yoki uyda davolash usulini tavsiya qilmang; har tavsifda '⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi.' qatori bo'lsin.

Siz video dvigateli uchun epizod JSON fayllarini yozasiz. Dvigatel faqat quyidagilarni tushunadi — boshqa quruvchi, parametr, sahna turi ishlatmang.

Quruvchilar (assets[*].build) va parametrlari — FAQAT shular:
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
- sprite: params.kind = bact_g|bact_p|sugar|soda|lemon|brush|candy (kichik obyektlar, "samples": 24).

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
- Karies tishni qanday yeydi
- Milk nega qonaydi: tish toshi
- Implant qanday qo'yiladi
- Breket tishni qanday suradi
- Tishni oqartirish: soda va limon xavfi
- Kanal davolash ichidan
- Aql tishi nega muammo
- Sut tishini nega davolash kerak
- Tishni to'g'ri yuvish
- Gazli ichimlik tishga nima qiladi

Namuna epizodlar (format va uslub aynan shunday bo'lsin):
```json
[
 {
  "id": "e01_karies",
  "num": 1,
  "series": "Tish sirlari",
  "title": "Karies tishni qanday yeydi",
  "assets": {
   "turn": {
    "build": "molar",
    "params": {
     "spot": true
    },
    "turn": {
     "frames": 24,
     "from": -40,
     "to": 120
    }
   },
   "healthy": {
    "build": "molar",
    "params": {}
   },
   "bact_g": {
    "build": "sprite",
    "params": {
     "kind": "bact_g"
    },
    "samples": 24
   },
   "bact_p": {
    "build": "sprite",
    "params": {
     "kind": "bact_p"
    },
    "samples": 24
   },
   "sugar": {
    "build": "sprite",
    "params": {
     "kind": "sugar"
    },
    "samples": 24
   },
   "s0": {
    "build": "section",
    "params": {}
   },
   "s1": {
    "build": "section",
    "params": {
     "caries": 1
    }
   },
   "s2": {
    "build": "section",
    "params": {
     "caries": 2
    }
   },
   "s3": {
    "build": "section",
    "params": {
     "caries": 3,
     "pulp": "hot"
    }
   },
   "s4": {
    "build": "section",
    "params": {
     "caries": 2,
     "fill": true
    }
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.4,
    "img": "turn",
    "pos": [
     540,
     1150
    ],
    "zoom": [
     1.0,
     1.2
    ],
    "ring": [
     540,
     790
    ],
    "lines": [
     [
      "Shu *kichkina nuqta*",
      84,
      "teal"
     ],
     [
      "tishingizni ichidan",
      70,
      "teal"
     ],
     [
      "*yeb qo'yadi*",
      92,
      "coral"
     ]
    ]
   },
   {
    "type": "cause",
    "dur": 5.2,
    "img": "turn",
    "pos": [
     540,
     1320
    ],
    "scale": 1.0,
    "falling": [
     "sugar",
     "sugar",
     "sugar"
    ],
    "crawlers": [
     "bact_g",
     "bact_p",
     "bact_p",
     "bact_g"
    ],
    "drops": "#aae63c",
    "lines": [
     [
      "Shakar + bakteriya",
      76,
      "teal"
     ],
     [
      "= *kislota*",
      92,
      "coral",
      2.2
     ]
    ]
   },
   {
    "type": "stages",
    "steps": [
     {
      "img": "s0",
      "dur": 3.8,
      "view": [
       1.2,
       "crown"
      ],
      "badge": [
       "TISH ICHIDA",
       "teal"
      ],
      "lines": [
       [
        "3 qavatdan iborat",
        76,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "label",
        "at": "enamel",
        "text": "Emal",
        "color": "teal",
        "to": [
         330,
         700
        ],
        "delay": 0.9
       },
       {
        "kind": "label",
        "at": "dentin",
        "text": "Dentin",
        "color": "dentin",
        "to": [
         330,
         930
        ],
        "delay": 1.5
       },
       {
        "kind": "label",
        "at": "pulp",
        "text": "Pulpa (nerv)",
        "color": "coral",
        "to": [
         760,
         800
        ],
        "side": "right",
        "delay": 2.1
       }
      ]
     },
     {
      "img": "s1",
      "dur": 4.2,
      "view": [
       2.0,
       "crown"
      ],
      "badge": [
       "1-BOSQICH · EMAL",
       "amber"
      ],
      "lines": [
       [
        "Og'rimaydi, shuning uchun",
        64,
        "teal"
       ],
       [
        "*sezilmaydi*",
        84,
        "amber"
       ]
      ],
      "fx": [
       {
        "kind": "ring",
        "at": "car1",
        "color": "amber",
        "delay": 1.2
       }
      ]
     },
     {
      "img": "s2",
      "dur": 4.4,
      "view": [
       2.0,
       "crown"
      ],
      "badge": [
       "2-BOSQICH · DENTIN",
       "orange"
      ],
      "lines": [
       [
        "Shirin va sovuqdan",
        66,
        "teal"
       ],
       [
        "*sanchiq* paydo bo'ladi",
        74,
        "orange"
       ]
      ],
      "fx": [
       {
        "kind": "bolts",
        "at": "car2",
        "color": "orange"
       }
      ]
     },
     {
      "img": "s3",
      "dur": 4.8,
      "view": [
       1.55,
       "pulp"
      ],
      "badge": [
       "3-BOSQICH · PULPA",
       "coral"
      ],
      "lines": [
       [
        "Kuchli og'riq —",
        72,
        "teal"
       ],
       [
        "*kanal davolash* kerak",
        70,
        "coral"
       ]
      ],
      "fx": [
       {
        "kind": "glow",
        "at": "pulp",
        "dy": 40,
        "delay": 0.8
       },
       {
        "kind": "bolts",
        "at": "pulp",
        "color": "coral",
        "r": 250,
        "size": 58,
        "n": 5
       },
       {
        "kind": "shake"
       }
      ]
     },
     {
      "img": "s4",
      "dur": 4.4,
      "view": [
       2.0,
       "crown"
      ],
      "badge": [
       "YECHIM",
       "teal"
      ],
      "lines": [
       [
        "Erta aniqlansa —",
        72,
        "teal"
       ],
       [
        "*bitta tashrif*, plomba",
        70,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "sparkle",
        "at": "car2"
       }
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.8,
    "img": "healthy",
    "pos": [
     540,
     900
    ],
    "scale": 0.95,
    "center": "crown",
    "lines": [
     [
      "Har *6 oyda*",
      84,
      "teal"
     ],
     [
      "stomatolog ko'rigidan o'ting",
      58,
      "teal"
     ]
    ]
   }
  ],
  "instagram": "Shu kichkina qora nuqta tishingizni ichidan yeb qo'yadi 🦷\n\nKaries 3 bosqichda rivojlanadi: avval emalda (og'rimaydi), keyin dentinda (shirin va sovuqdan sanchiydi), oxiri pulpada — kuchli og'riq va kanal davolash. Erta aniqlansa, oddiy plomba yetarli.\n\n💬 Oxirgi marta stomatologga qachon borgansiz?\n📍 Olmaliq\n\n⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi.\n\n#olmaliq #almalyk #toshkentviloyati #stomatologiya #tishlar #sogliq #3d #ai_doxtir",
  "tags": [
   "stomatologiya",
   "sogliq"
  ]
 },
 {
  "id": "e02_tish_toshi",
  "num": 2,
  "series": "Tish sirlari",
  "title": "Milk nega qonaydi: tish toshi",
  "assets": {
   "hero": {
    "build": "molar",
    "params": {
     "tartar": true
    }
   },
   "bact_g": {
    "build": "sprite",
    "params": {
     "kind": "bact_g"
    },
    "samples": 24
   },
   "bact_p": {
    "build": "sprite",
    "params": {
     "kind": "bact_p"
    },
    "samples": 24
   },
   "candy": {
    "build": "sprite",
    "params": {
     "kind": "candy"
    },
    "samples": 24
   },
   "g0": {
    "build": "section",
    "params": {}
   },
   "g1": {
    "build": "section",
    "params": {
     "tartar": 1
    }
   },
   "g2": {
    "build": "section",
    "params": {
     "tartar": 2,
     "gum": "red"
    }
   },
   "g3": {
    "build": "section",
    "params": {
     "tartar": 2,
     "gum": "recede",
     "gum_red": true,
     "bone_drop": 0.35
    }
   },
   "g4": {
    "build": "section",
    "params": {}
   }
  },
  "scenes": [
   {
    "type": "hook",
    "dur": 3.4,
    "img": "hero",
    "pos": [
     540,
     1170
    ],
    "zoom": [
     1.05,
     1.2
    ],
    "center": "crown",
    "lines": [
     [
      "Milk *qonayaptimi*?",
      84,
      "coral"
     ],
     [
      "Bu tish toshining",
      66,
      "teal"
     ],
     [
      "*birinchi signali*",
      84,
      "coral"
     ]
    ]
   },
   {
    "type": "cause",
    "dur": 4.8,
    "img": "hero",
    "pos": [
     540,
     1330
    ],
    "scale": 1.0,
    "center": "crown",
    "falling": [
     "candy",
     "candy"
    ],
    "crawlers": [
     "bact_g",
     "bact_p",
     "bact_g",
     "bact_p"
    ],
    "eat": false,
    "lines": [
     [
      "Ovqat qoldig'i + bakteriya",
      62,
      "teal"
     ],
     [
      "= *karash*",
      88,
      "amber",
      2.0
     ]
    ]
   },
   {
    "type": "stages",
    "steps": [
     {
      "img": "g0",
      "dur": 3.4,
      "view": [
       1.4,
       "crown"
      ],
      "badge": [
       "SOG'LOM MILK",
       "teal"
      ],
      "lines": [
       [
        "Milk tishni *mahkam* quchoqlaydi",
        60,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "label",
        "at": "gum",
        "text": "Milk",
        "color": "coral",
        "to": [
         300,
         760
        ],
        "delay": 0.8
       },
       {
        "kind": "label",
        "at": "bone",
        "text": "Suyak",
        "color": "dentin",
        "to": [
         300,
         1150
        ],
        "delay": 1.3
       }
      ]
     },
     {
      "img": "g1",
      "dur": 4.0,
      "view": [
       1.6,
       "crown"
      ],
      "badge": [
       "1 · KARASH",
       "amber"
      ],
      "lines": [
       [
        "Yumshoq qatlam —",
        70,
        "teal"
       ],
       [
        "*cho'tka bilan* ketadi",
        70,
        "amber"
       ]
      ],
      "fx": [
       {
        "kind": "ring",
        "at": "tartar_r",
        "color": "amber",
        "r": 80
       }
      ]
     },
     {
      "img": "g2",
      "dur": 4.4,
      "view": [
       1.6,
       "crown"
      ],
      "badge": [
       "2 · TISH TOSHI",
       "orange"
      ],
      "lines": [
       [
        "Qotib *toshga* aylanadi,",
        66,
        "orange"
       ],
       [
        "milk qizarib qonaydi",
        62,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "ring",
        "at": "tartar_r",
        "color": "orange",
        "r": 80
       },
       {
        "kind": "glow",
        "at": "gum",
        "color": "coral",
        "r": 140,
        "delay": 1.4
       }
      ]
     },
     {
      "img": "g3",
      "dur": 4.6,
      "view": [
       1.4,
       "crown"
      ],
      "badge": [
       "3 · PARODONTIT",
       "coral"
      ],
      "lines": [
       [
        "Milk va suyak *pasayadi*",
        66,
        "coral"
       ],
       [
        "tish qimirlay boshlaydi",
        62,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "arrow",
        "from": "tartar_r",
        "at": "bone",
        "color": "coral"
       },
       {
        "kind": "shake"
       }
      ]
     },
     {
      "img": "g4",
      "dur": 4.2,
      "view": [
       1.6,
       "crown"
      ],
      "badge": [
       "YECHIM",
       "teal"
      ],
      "lines": [
       [
        "*Professional tozalash*",
        70,
        "teal"
       ],
       [
        "yiliga 1–2 marta",
        64,
        "teal"
       ]
      ],
      "fx": [
       {
        "kind": "sparkle",
        "at": "tartar_r"
       }
      ]
     }
    ]
   },
   {
    "type": "cta",
    "dur": 4.6,
    "img": "g4",
    "pos": [
     540,
     980
    ],
    "scale": 1.0,
    "center": "crown",
    "lines": [
     [
      "Tishni *kuniga 2 marta*",
      74,
      "teal"
     ],
     [
      "va tish ipi bilan tozalang",
      58,
      "teal"
     ]
    ]
   }
  ],
  "instagram": "Tish yuvganda milk qonaydimi? Bu — tish toshining birinchi signali 🩸\n\nYumshoq karash vaqtida tozalanmasa, qotib toshga aylanadi. Tosh milkni qizartiradi, keyin milk va suyak pasayib, tish qimirlay boshlaydi (parodontit). Toshni faqat stomatolog professional tozalash bilan oladi.\n\n💬 Sizda ham milk qonaganmi?\n📍 Olmaliq\n\n⚠️ Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi.\n\n#olmaliq #almalyk #toshkentviloyati #stomatologiya #tishlar #sogliq #3d #ai_doxtir #parodontit",
  "tags": [
   "stomatologiya",
   "sogliq"
  ]
 }
]
```

Vazifa: 10 ta YANGI epizod yozing (series: "Tish sirlari"). Faktlarni veb-qidiruvda tekshiring.
"id" va "num" ni yozmasangiz ham bo'ladi — dastur o'zi raqamlaydi.
Javobni bitta ```json blokida {"episodes": [ ... ]} ko'rinishida qaytaring.
