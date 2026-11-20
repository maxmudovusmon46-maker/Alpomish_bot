import os
from flask import Flask, request
import telebot
from telebot import types
from google import genai
from google.genai import types as gemini_types

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_KALIT = os.environ.get("GEMINI_KALIT", "")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_KALIT)
app = Flask(__name__)

MODELLAR = {
    "🔵 Gemini Flash (Tezkor)": "gemini-3.1-flash-lite",
    "🟢 Gemini Pro (Aqlli)": "gemini-3.5-flash",
    "🟠 Hydrogen SI (Yangi)": "gemini-4-hydrogen"
}

tanlangan_si = {}
XARAKTER = "Sening isming Alpomish. O'zbek tilida aqlli, qisqa va do'stona javob ber. Seni Usmon yaratgan."

def tugmalar_menyusi():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔵 Gemini Flash (Tezkor)")
    markup.row("🟢 Gemini Pro (Aqlli)", "🟠 Hydrogen SI (Yangi)")
    return markup

@bot.message_handler(commands=['start'])
def salomlashish(xabar):
    tanlangan_si[xabar.chat.id] = "🔵 Gemini Flash (Tezkor)"
    bot.send_message(
        xabar.chat.id,
        "Assalomu alaykum! Men Alpomishman. Pastdagi tugmalardan modelni tanlang va savolingizni yozing:",
        reply_markup=tugmalar_menyusi()
    )

@bot.message_handler(func=lambda message: True)
def javob_berish(xabar):
    user_id = xabar.chat.id
    matn = xabar.text

    if matn in MODELLAR:
        tanlangan_si[user_id] = matn
        bot.reply_to(xabar, f"Ajoyib! Endi sizga **{matn}** javob beradi. Savolingizni yozing:", parse_mode="Markdown")
        return

    joriy_si = tanlangan_si.get(user_id, "🔵 Gemini Flash (Tezkor)")
    model_id = MODELLAR[joriy_si]
    bot.send_chat_action(user_id, 'typing')

    try:
        javob = client.models.generate_content(
            model=model_id,
            contents=matn,
            config=gemini_types.GenerateContentConfig(system_instruction=XARAKTER)
        )
        bot.reply_to(xabar, javob.text)
    except Exception as e:
        bot.reply_to(xabar, f"Xatolik: {str(e)[:100]}")

@app.route('/webhook', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://onrender.com")
    return "Alpomish Webhook muvaffaqiyatli ulandi!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
