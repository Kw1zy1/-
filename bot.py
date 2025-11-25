
# bot.py — Telegram bot
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8432636635:AAFun--AOKHOY6EgOmTApKTn7_GJ765IJmk"
ADMIN_CHAT_ID = 7749088892

user_cooldown = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = "Бот работает. Отправьте фото + текст."
    await update.message.reply_text(start_text)

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с фото"""
    user_id = update.effective_user.id
    current_time = datetime.now()
    
    # Проверка кулдауна (20 минут)
    if user_id in user_cooldown:
        time_diff = current_time - user_cooldown[user_id]
        if time_diff < timedelta(minutes=20):
            remaining = timedelta(minutes=20) - time_diff
            minutes = int(remaining.seconds / 60)
            seconds = remaining.seconds % 60
            await update.message.reply_text(f"❌ Новое объявление можно отправить через {minutes}м {seconds}с")
            return

    # Проверка наличия подписи
    if not update.message.caption:
        await update.message.reply_text("❌ Добавьте текст объявления к фотографии (длина текста не менее 10 символов)")
        return

    # Проверка длины текста
    if len(update.message.caption) < 10:
        await update.message.reply_text("❌ Текст объявления должен содержать минимум 10 символов")
        return

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Ошибка: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_photo_message))
    app.add_handler(MessageHandler(filters.ALL, handle_invalid_message))
    app.add_error_handler(error_handler)

    print("Bot started…")
    app.run_polling()

if __name__ == "__main__":
    main()
