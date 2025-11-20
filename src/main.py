import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Automatically read from Render environment variables (the ones you added in Render dashboard)
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Conversation states
(NAME, PHONE, BUILDING, MESSAGE) = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = (user.language_code or 'ro').lower()

    if 'ru' in lang:
        text = (
            "Привет! 👋\n"
            "Я бот DroneWash.md — профессиональная мойка фасадов, высотных зданий и солнечных панелей дронами в Молдове.\n\n"
            "Чем могу помочь?"
        )
        keyboard = [["Услуги", "Заказать мойку"]]
    else:
        text = (
            "Bună! 👋\n"
            "Sunt botul DroneWash.md — curățare profesională cu drona pentru fațade, clădiri înalte și panouri solare în Moldova.\n\n"
            "Cu ce te pot ajuta?"
        )
        keyboard = [["Servicii", "Solicită ofertă gratuită"]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        text = (
            "Наши услуги:\n\n"
            "▸ Мойка стеклянных фасадов и окон\n"
            "▸ Мойка солнечных панелей (крыши и фермы)\n"
            "▸ Наружная мойка зданий без лесов\n\n"
            "Цена от 3–8 лей/м² · Точная стоимость после бесплатного осмотра дроном\n\n"
            "Нажмите «Заказать мойку», чтобы оставить заявку!"
        )
    else:
        text = (
            "Serviciile noastre:\n\n"
            "▸ Curățare fațade de sticlă și geamuri la înălțime\n"
            "▸ Spălare panouri solare (acoperișuri și ferme)\n"
            "▸ Curățare exterioară clădiri fără schele\n\n"
            "Preț de la 3–8 lei/m² · Ofertă exactă după inspecția gratuită cu drona\n\n"
            "Apasă «Solicită ofertă gratuită» pentru cerere!"
        )
    await update.message.reply_text(text)

async def request_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        await update.message.reply_text("Как вас зовут?")
    else:
        await update.message.reply_text("Cum vă numiți?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        await update.message.reply_text("Номер телефона (с +373):")
    else:
        await update.message.reply_text("Numărul de telefon (cu +373):")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    keyboard = [
        ["Bloc de locuit / Жилой дом"],
        ["Clădire de birouri / Офис"],
        ["Hotel / Centru comercial"],
        ["Panouri solare / Солнечные панели"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        await update.message.reply_text("Тип объекта:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Tipul clădirii:", reply_markup=reply_markup)
    return BUILDING

async def get_building(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['building'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        await update.message.reply_text("Дополнительно (этажи, площадь, пожелания):")
    else:
        await update.message.reply_text("Detalii suplimentare (etaje, suprafață, dorințe):")
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['message'] = update.message.text
    user = update.effective_user

    lead = (
        "НОВАЯ ЗАЯВКА DroneWash.md \n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Объект: {context.user_data['building']}\n"
        f"Сообщение: {context.user_data['message']}\n"
        f"От: @{user.username or '—'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=lead)

    lang = (update.effective_user.language_code or 'ro').lower()
    if 'ru' in lang:
        await update.message.reply_text("Спасибо! Мы свяжемся с вами в ближайшие 30 минут! ")
    else:
        await update.message.reply_text("Mulțumim! Vă contactăm în maxim 30 de minute! ")

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
