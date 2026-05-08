import telebot
import requests
import os
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
AI_API_KEY = os.environ.get('AI_API_KEY')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

chat_history = {}

# ... function tanya_ai kau letak sini, sama je ...

@bot.message_handler(func=lambda message: True)
def balas_chat(message):
    user_id = message.from_user.id
    user_text = message.text
    ai_reply = tanya_ai(user_id, user_text)
    bot.reply_to(message, ai_reply)

# WEBHOOK ROUTES
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
