# AI Doxtir — 3D tibbiy videolar (@ai_doxtir × @ai_olmaliq)

Ikki kanal: **@ai_doxtir** (stomatologiya) va **@ai_olmaliq** (Olmaliq shahri). Har kuni **06:00 va 19:00** (Toshkent) da har bir kanalning navbatdagi epizodini **3D render qiladi → montaj qiladi → @ai_doxtirBot orqali video va tavsif matnini yuboradi**. Videoni Instagram'ga qo'lda joylaysiz, tavsifni botdan nusxalab qo'yasiz. Sxema geoilm bilan bir xil.

## Papkalar
```
run.py                 asosiy buyruq (navbat, render, yuborish)
config.json            handle, logo, muhr, oxirgi kadr matnlari, tavsif oxiri
sponsors.json          reklama beruvchilar (docs/REKLAMA.md)
episodes/*.json        10 ta epizod: 3D sahnalar, ekrandagi matnlar, Instagram tavsifi
engine/model3d.py      3D quruvchilar (Blender bpy, Cycles CPU)
engine/compose.py      montaj: sahnalar, reklama kartasi, musiqa → mp4
publishers/telegram.py botga video + tavsif yuborish
assets/logos/          logolar (SVG + PNG)       assets/sponsors/  hamkor logolari
docs/                  BRENDBUK.md, REKLAMA.md, OLMALIQ_SSENARIYLAR.md
data/sent.json         nima yuborilgan, hamkor hisobi
.github/workflows/     jadval (har kuni 19:30, zaxira 20:30)
.vscode/               VS Code: F5 bilan ishga tushirish menyusi
tools/make_episodes.py epizod JSON'larini yozadi
```

## Jadval va avtomatik ssenariylar
- `.github/workflows/ai_doxtir.yml`: render 05:35 / 18:35 da boshlanadi, video aniq **06:00 / 19:00** da yuboriladi (`run.py --send-at auto`). Zaxira: 06:20 / 19:20.
- Kanallar: `run.py` → `CHANNELS`. doxtir: `config.json`, `episodes/`, `data/sent.json`; olmaliq: `channels/olmaliq/config.json`, `channels/olmaliq/episodes/`, `data/sent_olmaliq.json`.
- **Qo'lda (API'siz):** `docs/SSENARIY_YOZISH.md` — Claude chatda `docs/PROMPT_*.md` bilan yozdirib, `inbox/<kanal>/` ga yuklaysiz.
- Ixtiyoriy: `ANTHROPIC_API_KEY` bo'lsa, navbat tugasa `tools/autogen.py` Claude API (veb-qidiruv bilan) orqali keyingi 10 ta ssenariyni yozadi, tekshiradi, navbatga qo'shadi va matnini botga ko'rib chiqish uchun yuboradi. Kerak: **`ANTHROPIC_API_KEY`** Secret.
- ai_olmaliq 3D sahnalari: `engine/olmaliq3d.py` (terrain, quarry, ore, flotation, globe, shaft, osprite). Boshlang'ich 10 epizod: `tools/make_olmaliq.py`.
- Globus teksturasi: NASA Blue Marble (public domain), `assets/textures/earth.jpg`.

## Bot nima yuboradi
1. **Video** — izohida tavsif matni to'liq (1024 belgigacha).
2. **📝 Tavsif** — bosib nusxa olinadigan blokda to'liq matn: hook, mazmun, savol, 📍 Olmaliq, disclaimer, heshteglar, hamkor qatori (bo'lsa), "Olmaliqdan — Olmaliq uchun".
3. Eslatma: geoteg Olmaliq, Collab @ai_olmaliq.

## GitHub'da o'rnatish (bir marta)
1. GitHub'da yangi repo: `ai-doxtir` (Private bo'lishi mumkin).
2. Fayllarni yuklang (`git push` yoki saytda *Add file → Upload files*). `.github` va `.vscode` papkalari ham borligini tekshiring.
3. **Settings → Secrets and variables → Actions**:
   - `TG_BOT_TOKEN` — @ai_doxtirBot tokeni (@BotFather)
   - `TG_MANUAL_CHAT_IDS` — Telegram ID raqamingiz (bir nechta bo'lsa vergul bilan)
   - `TG_ADMIN_CHAT_ID` — ixtiyoriy, xato xabarlari uchun (vergul bilan bir nechta)
   - `ANTHROPIC_API_KEY` — avtomatik ssenariy yozish uchun (console.anthropic.com)
4. @ai_doxtirBot'ga **/start** bosing.
5. **Settings → Actions → General → Workflow permissions → Read and write**.
6. Sinov: **Actions → AI Doxtir video → Run workflow**. ~15–20 daqiqada bot video yuboradi.

Jadval vaqtini `.github/workflows/ai_doxtir.yml` dagi `cron` qatorlarida va `run.py` → `SLOTS` da o'zgartirasiz (UTC = Toshkent − 5 soat).

## VS Code'da ishlash (lokal)
1. Python **3.13** o'rnating (Blender `bpy` faqat shu versiya bilan ishlaydi).
2. VS Code'da papkani oching → tavsiya etilgan kengaytmalarni o'rnating (Python, Debugpy).
3. Terminal: `python -m venv .venv` → aktivlashtiring → **Terminal → Run Task → "Kutubxonalarni o'rnatish"**.
4. `.env.example` dan nusxa olib `.env` yarating, token va ID ni yozing.
5. **F5 (Run and Debug)** menyusi:
   - **1) Tez sinov** — navbatdagi epizoddan 5 ta kadr (bir necha daqiqa)
   - **2) To'liq video** — epizodni tanlang, `out/` ga mp4 + tavsif .txt
   - **3) Yasash va botga yuborish**
   - **4) Reklama sinovi** — hamkor bilan kadrlar
   - **5) Navbat holati**

Kompyuterda videokarta bo'lmasa, to'liq video bir necha daqiqadan o'nlab daqiqagacha oladi — GitHub Actions'da yasash qulayroq.

## Reklama beruvchi
`sponsors.json` → `active: true` → push. Navbatdagi va yangi videolarga avtomatik qo'shiladi: o'rtada "REKLAMA" kartasi, pastda "Hamkor: …", oxirgi kadrda kontaktlar, tavsifda `#reklama` qatori. Batafsil: `docs/REKLAMA.md`.

## Yangi epizod
`tools/make_episodes.py` ichida yangi blok yozing (mavjudlaridan nusxa oling) → `python tools/make_episodes.py`. 3D sahna turlari: `section` (tish kesimi: karies, tosh, kanal, implant, sut tishi), `wisdom`, `front` (old tishlar), `molar`, `implant_parts`, `sprite` (bakteriya, shakar, gazli ichimlik, limon, cho'tka, konfet).

## Muhim
- Har bir videoda "Ma'lumot uchun. Tashxis va davolashni shifokor belgilaydi." yozuvi bor — olib tashlamang.
- Tibbiy matnlarni hamkor shifokorga tasdiqlatish tavsiya etiladi.
- Token va kalitlarni kodga yozmang — faqat `.env` va GitHub Secrets.
