from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import sqlite3

# Включаем логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '7927421241:AAGxALGJfjuBo0QVRQRla0V_T3KY1WUslv8'

CHANNEL_USERNAME = '@peepekss'

ADMIN_USERNAME = 'p1nemkl'

conn = sqlite3.connect('main.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    subscribed BOOLEAN DEFAULT FALSE
)
''')
conn.commit()

async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        cursor.execute('SELECT subscribed FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return True
        
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

def add_user_to_db(user_id: int, subscribed: bool):
    cursor.execute('INSERT OR REPLACE INTO users (user_id, subscribed) VALUES (?, ?)', (user_id, subscribed))
    conn.commit()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if await is_user_subscribed(user_id, context):
        keyboard = [
            ["Ник", "Кодер"],
            ["Помощь"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Вы подписаны! Выберите действие:", reply_markup=reply_markup)
    else:
        # Если пользователь не подписан, просим подписаться
        await update.message.reply_text("Пожалуйста, подпишитесь на канал https://t.me/peepekss, чтобы получить доступ.")

async def add_test_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("использование: /add_test_user <user_id>")
        return
    
    add_user_to_db(user_id, True)
    await update.message.reply_text(f"Пользователь с ID {user_id} добавлен как подписанный для тестирования.")


# Обработчик кнопки "Получить информацию 1"
async def info_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Мой ник: Dexivdlil")

# Обработчик кнопки "Получить информацию 2"
async def info_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Этого бота написал: https://t.me/p1nemkl")

# Обработчик кнопки "Помощь"
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Это помощь! Выберите одну из кнопок выше.")

# Основная функция для запуска бота
def main() -> None:
    # Создаем объект Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_test_user", add_test_user))

    # Регистрируем обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.Text(["Ник"]), info_1))
    application.add_handler(MessageHandler(filters.Text(["Кодер"]), info_2))
    application.add_handler(MessageHandler(filters.Text(["Помощь"]), help_command))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()