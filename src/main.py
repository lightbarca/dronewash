import os
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

(NAME, PHONE, BUILDING, MESSAGE) = range(4)

REMOVE = ReplyKeyboardRemove()

app = Flask(__name__)
@app.route('/')
def health():
    return "DroneWash.md bot is alive!", 200

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def get_lang(user):
    return (user.language_code or 'ro').lower()

# MAIN MENU – now fully bilingual from the first message
def main_menu(lang):
    if 'ru' in lang:
        return ReplyKeyboardMarkup([["Услуги", "Заказать мойку"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Servicii", "Solicită ofertă gratuită"]], resize_keyboard=True)

# SERVICES TEXT – fully bilingual
def services_text(lang):
    if 'ru' in lang:
        return (
            "Наши услуги:\n\n"
            "▸ Мойка стеклянных фасадов и окон высоток\n"
            "▸ Мойка солнечных панелей на крышах и фермах\n"
            "▸ Наружная мойка зданий без лесов\n\n"
            "Цена от 3–8 лей/м²\n"
            "Точная стоимость после бесплатного осмотра дроном\n\n"
            "Нажмите «Заказать мойку»"
        )
    return (
        "Serviciile noastre:\n\n"
        "▸ Curățare fațade de sticlă și geamuri la înălțime\n"
        "▸ Spălare panouri solare pe acoperișuri și ferme\n"
        "▸ Curățare exterioară clădiri fără schele\n\n"
        "Preț de la 3–8 lei/m²\n"
        "Ofertă exactă după inspecția gratuită cu drona\n\n"
        "Apasă «Solicită ofertă gratuită»"
    )

# All questions – fully bilingual from the start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user)
    text = "Привет! 👋\nЯ бот DroneWash.md — профессиональная мойка фасадов, высотных зданий и солнечных панелей дронами в Молдове.\n\nЧем могу помочь?" if 'ru' in lang else "Bună! 👋\nSunt botul DroneWash.md — curățare profesională cu drona pentru fațade, clădiri înalte și panouri solare în Moldova.\n\nCu ce te pot ajuta?"
    await update.message.reply_text(text, reply_markup=main_menu(lang))

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user)
    await update.message.reply_text(services_text(lang), reply_markup=main_menu(lang))

# The rest of the flow (request_quote, get_name, get_phone, get_building, get_message, cancel) stays the same as the last perfect version, but now the language is locked from the very first message

# ... (keep the rest of the handlers exactly as in the previous perfect code)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot_main()  # your existing bot_main() function with all handlers
