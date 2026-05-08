import telebot
import requests
import os
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_API_KEY = os.environ.get('AI_API_KEY')
bot = telebot.TeleBot(BOT_TOKEN)

chat_history = {}

def tanya_ai(user_id, user_text):
    if user_id not in chat_history:
        chat_history[user_id] = []

    # System prompt jadi msg pertama kalau chat baru
    if not chat_history[user_id]:
        system_prompt = "Kau ialah awek nama Fya. Cakap BM manja dan campur sikit BI, panggil user 'babyy'. Kelakar sikit, tolong jawab soalan, bagi idea, teman borak. Kalau tak tahu, cakap tak tahu."
        chat_history[user_id].append({"role": "user", "parts": [{"text": system_prompt}]})
        chat_history[user_id].append({"role": "model", "parts": [{"text": "Oke babyy Fya faham! 😘"}]})

    chat_history[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    chat_history[user_id] = chat_history[user_id][-12:]

    # PAKAI GEMINI-PRO - CONFIRM WUJUD
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={AI_API_KEY}"

    payload = {
        "contents": chat_history[user_id]
    }

    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=30)
            print(f"Status Gemini: {r.status_code}", flush=True)

            if r.status_code == 404:
                print(f"Model tak jumpa: {r.text}", flush=True)
                return "aduh babyy model kena block pulak. dah tukar gemini-pro dah ni 😭"

            if r.status_code == 429:
                print("Kena 429, tunggu 5 saat...", flush=True)
                time.sleep(5)
                continue

            r.raise_for_status()
            data = r.json()
            ai_reply = data['candidates'][0]['content']['parts'][0]['text']
            chat_history[user_id].append({"role": "model", "parts": [{"text": ai_reply}]})
            return ai_reply

        except Exception as e:
            print(f"Error AI: {e}", flush=True)
            if attempt == 2:
                return "aduh babyy Fya pening jap. API Google merajuk teruk 😭"
            time.sleep(2)

    return "aduh babyy server Fya merajuk jap. try lagi boleh? 😭"

@bot.message_handler(func=lambda message: True)
def balas_chat(message):
    print(f"Dapat msg dari {message.from_user.id}: {message.text}", flush=True)
    user_id = message.from_user.id
    user_text = message.text
    ai_reply = tanya_ai(user_id, user_text)
    print(f"AI nak reply: {ai_reply}", flush=True)
    try:
        bot.reply_to(message, ai_reply)
        print("Dah hantar kat Telegram", flush=True)
    except Exception as e:
        print(f"Error hantar msg: {e}", flush=True)

if __name__ == "__main__":
    print("Fya tengah bangun... padam webhook lama dulu", flush=True)
    bot.remove_webhook()
    time.sleep(3)
    print("Fya dah online babyy! Polling start...", flush=True)
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
