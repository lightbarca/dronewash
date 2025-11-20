import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

(NAME, PHONE, BUILDING, MESSAGE) = range(4)

REMOVE = ReplyKeyboardRemove()

def get_lang(user):
    code = user.language_code or 'ro'
    return 'ru' if code.lower().startswith('ru') else 'ro'

# Store language once at start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user)
    context.user_data['lang'] = lang

    if lang == 'ru':
        text = "Привет! 👋\nЯ бот DroneWash.md — профессиональная мойка фасадов, высотных зданий и солнечных панелей дронами в Молдове.\n\nЧем могу помочь?"
        kb = [["Услуги", "Заказать мойку"]]
    else:
        text = "Bună! 👋\nSunt botul DroneWash.md — curățare profesională cu drona pentru fațade, clădiri înalte și panouri solare în Moldova.\n\nCu ce te pot ajuta?"
        kb = [["Servicii", "Solicită ofertă gratuită"]]

    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'ro')
    if lang == 'ru':
        text = ("Наши услуги:\n\n"
                "▸ Мойка стеклянных фасадов и окон\n"
                "▸ Мойка солнечных панелей\n"
                "▸ Наружная мойка зданий без лесов\n\n"
                "Цена от 3–8 лей/м²")
    else:
        text = ("Serviciile noastre:\n\n"
                "▸ Curățare fațade de sticlă și geamuri\n"
                "▸ Spălare panouri solare\n"
                "▸ Curățare exterioară clădiri fără schele\n\n"
                "Preț de la 3–8 lei/m²")

    await update.message.reply_text(text, reply_markup=main_menu(lang))

def main_menu(lang):
    if lang == 'ru':
        return ReplyKeyboardMarkup([["Услуги", "Заказать мойку"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Servicii", "Solicită ofertă gratuită"]], resize_keyboard=True)

async def request_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data['lang']
    text = "Как вас зовут?" if lang == 'ru' else "Cum vă numiți?"
    kb = [["Anulează" if lang == 'ro' else "Отмена"]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["Anulează", "Отмена"]:
        return await cancel(update, context)
    context.user_data['name'] = update.message.text
    lang = context.user_data['lang']
    text = "Номер телефона (с +373):" if lang == 'ru' else "Numărul de telefon (cu +373):"
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([["Anulează" if lang == 'ro' else "Отмена"]], resize_keyboard=True))
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["Anulează", "Отмена"]:
        return await cancel(update, context)
    context.user_data['phone'] = update.message.text
    lang = context.user_data['lang']
    kb = [
        ["Bloc de locuit / Жилой дом"],
        ["Clădire de birouri / Офис"],
        ["Hotel / Centru comercial"],
        ["Panouri solare / Солнечные панели"],
        ["Anulează" if lang == 'ro' else "Отмена"]
    ]
    await update.message.reply_text("Tipul clădirii:" if lang == 'ro' else "Тип объекта:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return BUILDING

async def get_building(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["Anulează", "Отмена"]:
        return await cancel(update, context)
    context.user_data['building'] = update.message.text
    lang = context.user_data['lang']
    text = "Detalii suplimentare (etaje, suprafață, dorințe):" if lang == 'ro' else "Дополнительно (этажи, площадь, пожелания):"
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([["Anulează" if lang == 'ro' else "Отмена"]], resize_keyboard=True))
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["Anulează", "Отмена"]:
        return await cancel(update, context)
    context.user_data['message'] = update.message.text
    user = update.effective_user
    lang = context.user_data['lang']

    lead = (
        "NOUĂ CERERE DroneWash.md \n\n"
        f"Nume: {context.user_data['name']}\n"
        f"Telefon: {context.user_data['phone']}\n"
        f"Obiect: {context.user_data['building']}\n"
        f"Mesaj: {context.user_data['message']}\n"
        f"De la: @{user.username or '—'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=lead)

    thank = "Mulțumim! Vă contactăm în maxim 30 de minute! 🚁" if lang == 'ro' else "Спасибо! Мы свяжемся с вами в ближайшие 30 минут! 🚁"
    await update.message.reply_text(thank, reply_markup=REMOVE)
    await update.message.reply_text("Ce mai pot face pentru dvs.?" if lang == 'ro' else "Что ещё могу сделать для вас?", reply_markup=main_menu(lang))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'ro')
    text = "Cererea a fost anulată." if lang == 'ro' else "Заявка отменена."
    await update.message.reply_text(text, reply_markup=main_menu(lang))
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Servicii|Услуги)$"), services))

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(Solicită ofertă gratuită|Заказать мойку)$"), request_quote)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            BUILDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_building)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Anulează|Отмена)$"), cancel)],
    )
    app.add_handler(conv)

    print("DroneWash.md bot is running as Background Worker...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
