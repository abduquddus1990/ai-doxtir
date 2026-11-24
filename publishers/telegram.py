"""Telegram: tayyor video + tavsif matnini @ai_doxtirBot orqali yuborish (qo'lda joylash rejimi).

Ketma-ketlik har bir chatga:
  1) video — izohida (caption) tavsif matni to'liq (1024 belgigacha), uzunroq bo'lsa qisqa sarlavha;
  2) "📝 Tavsif" — bosib nusxa olinadigan <pre> blokda to'liq matn (Instagram'ga qo'yish uchun);
  3) joylash eslatmasi.
"""
import os, requests

API = "https://api.telegram.org/bot{token}/{method}"

def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def notify(text):
    token = os.getenv("TG_BOT_TOKEN")
    chats = [c.strip() for c in os.getenv("TG_ADMIN_CHAT_ID", "").split(",") if c.strip()]
    if not token: return
    for chat in chats:
        try:
            requests.post(API.format(token=token, method="sendMessage"), data={"chat_id": chat, "text": text[:4000]}, timeout=30)
        except requests.RequestException:
            pass

def send_manual(path, ep, caption, chat_ids):
    token = os.environ["TG_BOT_TOKEN"]
    if not chat_ids: raise RuntimeError("TG_MANUAL_CHAT_IDS bo'sh")
    head = f"🦷 AI Doxtir — {ep.get('series', '')} #{ep.get('num', '')}: {ep['title']}"
    video_caption = caption if len(caption) <= 1024 else head + "\n\nTavsif matni pastda 👇"
    sent = 0
    for chat in chat_ids:
        with open(path, "rb") as f:
            r = requests.post(API.format(token=token, method="sendVideo"),
                              data={"chat_id": chat, "caption": video_caption, "supports_streaming": "true", "width": 1080, "height": 1920},
                              files={"video": f}, timeout=600)
        if not r.ok:
            print(f"⚠️ {chat}: {r.json().get('description')}")
            continue
        sent += 1
        requests.post(API.format(token=token, method="sendMessage"), timeout=30, data={
            "chat_id": chat, "parse_mode": "HTML",
            "text": f"<b>📝 Tavsif (bosib nusxa oling)</b>\n<pre>{_esc(caption)}</pre>"[:4096]}).raise_for_status()
        requests.post(API.format(token=token, method="sendMessage"), timeout=30, data={
            "chat_id": chat, "text": f"{head}\n📍 Geoteg: Olmaliq · 🤝 Collab: @ai_olmaliq · muqova: 1-soniya"})
    if not sent:
        raise RuntimeError("Hech bir chatga yuborilmadi — botga /start bosilganini tekshiring")
