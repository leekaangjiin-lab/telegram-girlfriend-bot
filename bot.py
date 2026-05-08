import telebot
import requests
import os
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_API_KEY = os.environ.get('AI_API_KEY')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

chat_history = {}

def tanya_ai(user_id, user_text):
    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    chat_history[user_id] = chat_history[user_id][-12:]

    system_prompt = "Kau ialah awek nama Fya. Cakap BM manja dan campur sikit BI, panggil user 'babyy'. Kelakar sikit, tolong jawab soalan, bagi idea, teman borak. Kalau tak tahu, cakap tak tahu."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"

    payload = {
        "contents": chat_history[user_id],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        print(f"Status Gemini: {r.status_code}") , flush=True)
        print(f"Response Gemini: {r.text}")
        r.raise_for_status()
        data = r.json()
        ai_reply = data['candidates'][0]['content']['parts'][0]['text']
        chat_history[user_id].append({"role": "model", "parts": [{"text": ai_reply}]})
        return ai_reply
    except Exception as e:
        print(f"Error AI: {e}")
        return "aduh babyy server Fya merajuk jap. try lagi boleh? 😭"

@bot.message_handler(func=lambda message: True)
def balas_chat(message):
    print(f"Dapat msg dari {message.from_user.id}: {message.text}") , flush=True) # LOG 1
    user_id = message.from_user.id
    user_text = message.text
    ai_reply = tanya_ai(user_id, user_text)
    print(f"AI nak reply: {ai_reply}") , flush=True) # LOG 2
    try:
        bot.reply_to(message, ai_reply)
        print("Dah hantar kat Telegram") # LOG 3
    except Exception as e:
        print(f"Error hantar msg: {e}") , flush=True) # LOG 4

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-girlfriend-bot-38ox.onrender.com/' + BOT_TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    print("Bot starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
