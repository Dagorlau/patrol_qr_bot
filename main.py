from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import pytz  # Добавлен для часового пояса

ADMINS = [1008592626, 1710339009, 670020154]

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
    if user.id in user_last_point:
        point_code, point_name = user_last_point.pop(user.id)

        # Устанавливаем саратовский часовой пояс
        timezone = pytz.timezone("Europe/Saratov")
        local_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"Охранник {user.full_name} прошёл точку: {point_name} ({point_code}) в {local_time}\n"
            f"Геолокация: https://www.google.com/maps?q={location.latitude},{location.longitude}"
        )
        for admin in ADMINS:
            await context.bot.send_message(chat_id=admin, text=message)
        await update.message.reply_text("Геолокация получена и передана.")
    else:
        await update.message.reply_text("Сначала просканируйте QR-код с командой /start.")

if __name__ == "__main__":
    app = ApplicationBuilder().token("8138530190:AAEUF6qsQO6P_j1htHRUQ5JXWFIW9G9d3Ws").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.run_polling()