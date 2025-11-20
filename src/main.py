import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

(NAME, PHONE, BUILDING, MESSAGE, CONFIRM) = range(5)

REMOVE = ReplyKeyboardRemove()

def main_menu(lang: str):
    if 'ru' in lang.lower():
        return ReplyKeyboardMarkup([["Услуги", "Заказать мойку"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Servicii", "Solicită ofertă gratuită"]], resize_keyboard=True)

def back_button(lang: str):
    if 'ru' in lang.lower():
        return ReplyKeyboardMarkup([["Назад", "Отмена"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([["Înapoi", "Anulează"]], resize_keyboard=True)

def building_keyboard(lang: str):
    kb = [
        ["Bloc de locuit / Жилой дом"],
        ["Clădire de birouri / Офис"],
        ["Hotel / Centru comercial"],
        ["Panouri solare / Солнечные панели"],
        ["Înapoi" if 'ro' in lang.lower() else "Назад"]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    text = "Привет! 👋\nЯ бот DroneWash.md — профессиональная мойка фасадов, высотных зданий и солнечных панелей дронами в Молдове.\n\nЧем могу помочь?" if 'ru' in lang else "Bună! 👋\nSunt botul DroneWash.md — curățare profesională cu drona pentru fațade, clădiri înalte și panouri solare în Moldova.\n\nCu ce te pot ajuta?"
    await update.message.reply_text(text, reply_markup=main_menu(lang))

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    text = "Наши услуги:\n\n▸ Мойка стеклянных фасадов и окон\n▸ Мойка солнечных панелей\n▸ Наружная мойка зданий без лесов\n\nЦена от 3–8 лей/м²\n\nНажмите «Заказать мойку», чтобы оставить заявку!" if 'ru' in lang else "Serviciile noastre:\n\n▸ Curățare fațade de sticlă și geamuri\n▸ Spălare panouri solare\n▸ Curățare exterioară clădiri fără schele\n\nPreț de la 3–8 lei/m²\n\nApasă «Solicită ofertă gratuită» pentru cerere!"
    await update.message.reply_text(text, reply_markup=main_menu(lang))

async def request_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Как вас зовут?" if 'ru' in lang else "Cum vă numiți?", reply_markup=back_button(lang))
    return NAME

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Revenit la meniul principal." if 'ro' in lang else "Вернулся в главное меню.", reply_markup=main_menu(lang))
    return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() in ["Înapoi", "Назад"]:
        return await request_quote(update, context)
    context.user_data['name'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Номер телефона (с +373):" if 'ru' in lang else "Numărul de telefon (cu +373):", reply_markup=back_button(lang))
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() in ["Înapoi", "Назад"]:
        return await request_quote(update, context)
    context.user_data['phone'] = update.message.text
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Тип объекта:" if 'ru' in lang else "Tipul clădirii:", reply_markup=building_keyboard(lang))
    return BUILDING

async def get_building(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in ["Înapoi", "Назад"]:
        return await get_phone(update, context)
    context.user_data['building'] = text
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Дополнительно (этажи, площадь, пожелания):" if 'ru' in lang else "Detalii suplimentare (etaje, suprafață, dorințe):", reply_markup=back_button(lang))
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() in ["Înapoi", "Назад"]:
        return await get_building(update, context)
    context.user_data['message'] = update.message.text
    user = update.effective_user
    lang = (user.language_code or 'ro').lower()

    lead = (
        "NOUĂ CERERE DroneWash.md \n\n"
        f"Nume: {context.user_data['name']}\n"
        f"Telefon: {context.user_data['phone']}\n"
        f"Obiect: {context.user_data['building']}\n"
        f"Mesaj: {context.user_data['message']}\n"
        f"De la: @{user.username or '—'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=lead)

    await update.message.reply_text(
        "Спасибо! Мы свяжемся с вами в ближайшие 30 минут! 🚁" if 'ru' in lang else
        "Mulțumim! Vă contactăm în maxim 30 de minute! 🚁",
        reply_markup=REMOVE
    )
    await update.message.reply_text("Ce mai pot face pentru dvs.?", reply_markup=main_menu(lang))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = (update.effective_user.language_code or 'ro').lower()
    await update.message.reply_text("Cererea a fost anulată." if 'ro' in lang else "Заявка отменена.", reply_markup=main_menu(lang))
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
        fallbacks=[
            MessageHandler(filters.Regex("^(Anulează|Отмена)$"), cancel),
            MessageHandler(filters.Regex("^(Înapoi|Назад)$"), back_to_start),  # works as universal back
        ],
    )
    app.add_handler(conv_handler)

    print("DroneWash.md bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
