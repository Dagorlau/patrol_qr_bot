from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import os

ADMINS = [1008592626]

checkpoints = {
    'door_001': {'name': 'Гараж'},
    'door_002': {'name': 'Склад 3'},
    'door_003': {'name': 'Склад 4'},
    'door_004': {'name': 'Склад 5'},
    'door_005': {'name': 'Склад 6'},
}

user_last_point = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args:
        point_code = context.args[0].lower()
        if point_code in checkpoints:
            point_name = checkpoints[point_code]['name']
            user_last_point[user.id] = (point_code, point_name)
            keyboard = [[KeyboardButton("Отправить геолокацию", request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                f"Вы прошли точку: {point_name}. Пожалуйста, отправьте свою геолокацию.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Неизвестный код точки.")
    else:
        await update.message.reply_text("QR-код не содержит код точки. Пример: /start door_001")

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    location = update.message.location
    if not location:
        await update.message.reply_text("Ошибка: Геолокация не получена. Пожалуйста, попробуйте ещё раз.")
        return
    if user.id in user_last_point:
        point_code, point_name = user_last_point.pop(user.id)
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"Охранник {user.full_name} прошёл точку: {point_name} ({point_code}) в {time}\n"
            f"Геолокация: https://www.google.com/maps?q={location.latitude},{location.longitude}"
        )
        for admin in ADMINS:
            await context.bot.send_message(chat_id=admin, text=message)
        await update.message.reply_text("Геолокация получена и передана.")
    else:
        await update.message.reply_text("Сначала просканируйте QR-код с командой /start.")

if name == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")  # лучше токен брать из переменной окружения
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.run_polling()