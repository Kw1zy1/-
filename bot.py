
# bot.py — Telegram bot
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
BOT_TOKEN = "8432636635:AAFun--AOKHOY6EgOmTApKTn7_GJ765IJmk"
ADMIN_CHAT_ID = 7749088892

# Хранилище данных
user_cooldown = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    start_text = """Здравствуйте❕

В данном боте вы можете предложить свое объявление, но оно будет опубликовано только при соблюдении ряда правил:
1️⃣ Прикрепите только ОДНУ фотографию (не добавляйте больше одного фото)
2️⃣ Добавьте текст объявления к данной фотографии (фото + текст необходимо отправить вместе, а не двумя разными сообщениями)
3️⃣ Один пользователь может предложить только одно объявление в 20 минут

ВАЖНО❗️Перед публикацией объявления перейдите в Настройки Telegram - Конфиденциальность - Пересылка сообщений - выберите Все
Если у вас стоит запрет на пересылку сообщений для всех, то Telegram не даст нам опубликовать ваш пост.

Коммерческие посты публикуются только на платной основе, к ним относится: 
▫️оптовая продажа, 
▫️продажа нового товара, 
▫️продажа одноразок и жидкостей (дабы если это одна одноразка или одна жидкость), 
▫️реклама магазина / вейпшопа

Если вы хотите приобрести рекламу, обращайтесь - @Manager_Greshnik

В боте лимит на подачу объявлений 20 минут 

Объявление должно быть в виде 1 фотографии и текста не меньше 10 символов"""

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

    # Формирование сообщения для администратора
    username = f"@{update.effective_user.username}" if update.effective_user.username else "Не указан"
    user_profile_link = f"tg://user?id={user_id}"
    
    caption = f"{update.message.caption}\n\nНаписать автору: [{username}]({user_profile_link})"

    disclaimer = """\n\n**Важно!** Не переводите деньги за
предоплату, бронирование
устройства или на проезд. Будьте
бдительны — не ведитесь на уловки 
мошенников.

**Канал несет исключительно
информационный характер.
Никотин вызывает зависимость.
18+**"""
    full_text = caption + disclaimer

    try:
        # Создаем клавиатуру с кнопками ДЛЯ АДМИНИСТРАТОРА
        admin_keyboard = [
            [InlineKeyboardButton("Подать объявление", url="https://t.me/gfdhfghgfhghgfbot")],
            [InlineKeyboardButton("Реклама", url="https://t.me/Manager_Greshnik")]
        ]
        admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)
        
        # Отправка администратору с кнопками
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=full_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_reply_markup
        )
        # Обновление времени последнего объявления
        user_cooldown[user_id] = current_time
        
        # Отправляем пользователю сообщение БЕЗ кнопок
        await update.message.reply_text("✅ Объявление отправлено на модерацию! Ожидайте публикации.")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения администратору: {e}")
        await update.message.reply_text("❌ Произошла ошибка при отправке объявления. Попробуйте позже.")

async def handle_invalid_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик некорректных сообщений"""
    await update.message.reply_text(
        "❌ Пожалуйста, отправьте ОДНУ фотографию с текстовым описанием (длина текста не менее 10 символов)\n\n"
        "Фото и текст должны быть отправлены вместе в одном сообщении."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logging.error(f"Ошибка при обработке сообщения: {context.error}")

def main():
    """Основная функция запуска бота"""
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, handle_photo_message))
    application.add_handler(MessageHandler(filters.ALL, handle_invalid_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if name == "__main__":
    main()
