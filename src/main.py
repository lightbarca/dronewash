import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

(NAME, PHONE, BUILDING, MESSAGE) = range(4)

# Simple main menu keyboard
def main_keyboard(lang: str):
    if 'ru' in lang:
        return ReplyKeyboardMarkup([["Услуги", "Заказать мойку"]], resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup([["Servicii", "Solicită ofertă gratuită"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = (user.language_code or 'ro').lower()
    await update.message.reply_text(
        "Привет! 👋\nЯ бот DroneWash.md — профессиональная мойка фасадов, высотных зданий и солнечных панелей дронами в Молдове.\n\nЧем могу помочь?"
        if 'ru' in lang else
        "Bună! 👋\nSunt botul DroneWash.md — curățare profesională cu drona pentru fațade, clădiri înalte și panouri solare în Moldova.\n\nCu ce te pot ajuta?",
        reply_markup=main_keyboard(lang)
    )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    text = (
        "Наши услуги:\n\n"
        "▸ Мойка стеклянных фасадов и окон\n"
        "▸ Мойка солнечных панелей (крыши и фермы)\n"
        "▸ Наружная мойка зданий без лесов\n\n"
        "Цена от 3–8 лей/м² · Точная стоимость после бесплатного осмотра дроном\n\n"
        "Нажмите «Заказать мойку», чтобы оставить заявку!"
        if 'ru' in lang else
        "Serviciile noastre:\n\n"
        "▸ Curățare fațade de sticlă și geamuri la înălțime\n"
        "▸ Spălare panouri solare (acoperișuri și ferme)\n"
        "▸ Curățare exterioară clădiri fără schele\n\n"
        "Preț de la 3–8 lei/m² · Ofertă exactă după inspecția gratuită cu drona\n\n"
        "Apasă «Solicită ofertă gratuită» pentru cerere!"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard(lang))

async def request_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Как вас зовут?" if 'ru' in lang else "Cum vă numiți?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Номер телефона (с +373):" if 'ru' in lang else "Numărul de telefon (cu +373):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    keyboard = [
        ["Bloc de locuit / Жилой дом"],
        ["Clădire de birouri / Офис"],
        ["Hotel / Centru comercial"],
        ["Panouri solare / Солнечные панели"]
    ]
    await update.message.reply_text(
        "Тип объекта:" if 'ru' in (update.effective_user.language_code or 'ro').lower() else "Tipul clădirii:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return BUILDING

async def get_building(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['building'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Дополнительно (этажи, площадь, пожелания):" if 'ru' in lang else "Detalii suplimentare (etaje, suprafață, dorințe):")
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['message'] = update.message.text
    user = update.effective_user
    lang = (user.language_code or 'ro').lower()

    # Lead for you — always Romanian
    lead = (
        "NOUĂ CERERE DroneWash.md \n\n"
        f"Nume: {context.user_data['name']}\n"
        f"Telefon: {context.user_data['phone']}\n"
        f"Obiect: {context.user_data['building']}\n"
        f"Mesaj: {context.user_data['message']}\n"
        f"De la: @{user.username or '—'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=lead)

    # Final thank-you + clean keyboard
    await update.message.reply_text(
        "Спасибо! Мы свяжемся с вами в ближайшие 30 минут! 🚁" if 'ru' in lang else
        "Mulțumim! Vă contactăm în maxim 30 de minute! 🚁",
        reply_markup=main_keyboard(lang)  # brings back only the two main buttons
    )
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Servicii|Услуги)$"), services))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(Solicită ofertă gratuită|Заказать мойку)$"), request_quote)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            BUILDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_building)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    print("DroneWash.md bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
