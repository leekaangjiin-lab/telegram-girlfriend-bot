import os
import telebot
import requests
import threading
from flask import Flask

# 1. AMBIL TOKEN DARI ENVIRONMENT VARIABLE - JANGAN LETAK DIRECT
BOT_TOKEN = os.environ['BOT_TOKEN']
AI_API_KEY = os.environ['AI_API_KEY']

bot = telebot.TeleBot(BOT_TOKEN)
chat_history = {} # Simpan memory setiap user

# 2. FUNCTION PANGGIL AI - Guna Gemini sebab free
def tanya_ai(user_id, user_text):
    # Setup history untuk user ni
    if user_id not in chat_history:
        chat_history[user_id] = []

    # Tambah mesej user dalam history
    chat_history[user_id].append({"role": "user", "parts": [{"text": user_text}]})

    # Potong history kalau panjang sangat, jimat token
    chat_history[user_id] = chat_history[user_id][-12:]

    # System prompt = "perangai" bot kau
    system_prompt = "Kau ialah awek nama Fya. Cakap BM manja dan campur sikit BI, panggil user 'babyy'. Kelakar sikit, tolong jawab soalan, bagi idea, teman borak. Kalau tak tahu, cakap tak tahu."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={AI_API_KEY}"

    payload = {
        "contents": chat_history[user_id], # NI YANG SILAP TADI
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        ai_reply = data['candidates'][0]['content']['parts'][0]['text']

        # Simpan reply AI dalam history jugak
        chat_history[user_id].append({"role": "model", "parts": [{"text": ai_reply}]})
        return ai_reply

    except Exception as e:
        print(f"Error AI: {e}")
        return "aduh babyy, tak faham laa. try tanya lagi sekali boleh?"

# 3. HANDLE SEMUA MESEJ MASUK
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    bot.send_chat_action(user_id, 'typing') # bagi "typing..."
    reply = tanya_ai(user_id, user_text)
    bot.reply_to(message, reply)

# 4. COMMAND /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "hye babyy! Fya kat sinii. apa yang jadi harini?")

# 5. FLASK UNTUK UPTIMEROBOT PING - SUPAYA RENDER TAK TIDUR
app = Flask('')

@app.route('/')
def home():
    return "Fya Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 6. JALANKAN BOT & FLASK SERENTAK
print("Bot starting...")
threading.Thread(target=run_flask).start()
bot.polling(non_stop=True)
