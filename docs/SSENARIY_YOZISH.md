# Ssenariylarni qo'lda yuklash (Claude chat orqali, API'siz)

Navbatda har kanal uchun ssenariylar bor. Har kuni 2 tadan ketadi (06:00 va 19:00), ya'ni 10 ta ssenariy 5 kunga yetadi.
Navbat kamayganda bot eslatadi: "📥 Ssenariylar kam qoldi".

## 1. Claude chatda yozdirish
1. GitHub'da `docs/PROMPT_DOXTIR.md` (yoki `docs/PROMPT_OLMALIQ.md`) ni oching → matnini nusxalang.
2. claude.ai da yangi suhbat ochib, matnni yuboring. Claude 10 ta ssenariyni JSON qilib beradi.
3. Ko'proq kerak bo'lsa, o'sha suhbatda: **"yana 10 ta yoz, oldingilarini takrorlama"**.

## 2. GitHub'ga yuklash
1. Claude javobidagi JSON blokini nusxalang → kompyuterda `doxtir_1.json` kabi fayl qilib saqlang
   (Bloknot → Saqlash → "Kodlash: UTF-8", fayl turi: "Barcha fayllar").
2. GitHub → `abduquddus1990/ai-doxtir` → `inbox/doxtir/` (yoki `inbox/olmaliq/`) papkasi → **Add file → Upload files** → faylni tashlang → **Commit changes**.

## 3. Keyin nima bo'ladi
- Navbatdagi ishda (06:00 yoki 19:00 dan oldin) dastur faylni tekshiradi.
  To'g'ri ssenariylar navbatga qo'shiladi, matni botga **tanishib chiqish uchun** keladi.
  Xatosi borlari qabul qilinmaydi — bot sababini yozadi (Claude'ga shu xatoni ko'rsatib tuzattiring).
- Yuklangan fayl `inbox/<kanal>/done/` ga ko'chiriladi.

## Muhim
- Tibbiy va Olmaliq faktlarini yuklashdan oldin ko'z yugurtirib chiqing — video avtomatik chiqadi.
- Ssenariyni olib tashlash: `episodes/` (yoki `channels/olmaliq/episodes/`) dagi faylini o'chiring.
