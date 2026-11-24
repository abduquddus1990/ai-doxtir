# Reklama beruvchini videolarga qo'shish

Videolar yuborilish paytida yasaladi. Shuning uchun `sponsors.json` dagi faol hamkor **navbatda turgan va bundan keyin yasaladigan hamma videolarga** avtomatik qo'shiladi. Eski videolarni qayta yuklash kerak emas.

## 4 ta joylashuv (`placements`)
| Kod | Qayerda | Ko'rinishi |
|---|---|---|
| `mid` | Video o'rtasida (bosqichlar orasida), 3–4 s | "REKLAMA" belgili karta: logo, nom, shior, taklif, telefon, manzil, Telegram |
| `corner` | Reklama kartasidan keyingi kadrlarda | Pastda "Hamkor: [nom]" belgisi |
| `end` | Oxirgi kadr | Obuna o'rniga hamkorning nomi va kontaktlari ("REKLAMA" yozuvi bilan) |
| `caption` | Instagram tavsifi | "🤝 Hamkor: …", kontaktlar, `#reklama` |

Qaysilarini qo'shish — sotilgan paketga qarab tanlanadi (pastda).

## Qadamlar
1. Hamkor logosini (kvadrat PNG, kamida 500×500) `assets/sponsors/` papkasiga qo'ying.
2. `sponsors.json` da namunadan nusxa oling va to'ldiring:
   - `id` — lotincha, bo'sh joysiz (masalan `dent_olmaliq`)
   - `active: true`
   - `from` / `to` — reklama sanalari (YYYY-MM-DD)
   - `tags` — qaysi videolarga: `["stomatologiya"]` yoki bo'sh `[]` = hammasiga
   - `max_videos` — paketdagi video soni (tizim o'zi sanaydi: `data/sent.json` → `sponsor_counts`)
   - `color` — hamkor brend rangi (`#RRGGBB`)
3. Sinov (VS Code → "4) Reklama sinovi") yoki: `python run.py --episode e01_karies --quality preview --no-send --sponsor dent_olmaliq --preview-times 10,13,16,30`
4. GitHub'ga push qiling — keyingi jadval bo'yicha video hamkor bilan chiqadi.

Bir vaqtda bir nechta hamkor faol bo'lsa, ro'yxatda birinchi turgan (sanasi va tegi mos) tanlanadi. Paket tugasa (`max_videos`), keyingisiga o'tadi.

## Paketlar (taklif)
| Paket | Joylashuv | Nima beradi |
|---|---|---|
| Start | `caption` + `end` | Tavsifda va oxirgi kadrda kontakt |
| Standart | `mid` + `end` + `caption` | Video o'rtasidagi karta — eng ko'p ko'riladigan joy |
| Premium | hammasi + mavzuni hamkor tanlaydi | Hamkor yo'nalishidagi alohida epizod (masalan, ularning implant usuli) |

Narxni ko'rishlar statistikasiga (Instagram Insights → Olmaliq ulushi) qarab belgilang. Birinchi 1–2 hamkorga bepul yoki chegirma bilan bering — natijani keys sifatida keyingilariga ko'rsatasiz.

## Qonuniy talablar
- Reklama kartasi va tavsifda **"REKLAMA" / `#reklama`** belgisi doim turadi — olib tashlamang.
- Tibbiy reklama: hamkorning litsenziyasi bo'lishi, "100% kafolat" kabi va'dalar yozilmasligi kerak.
- `mid_text` (taklif) matnini hamkor bilan yozma kelishib oling.
