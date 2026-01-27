import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton(
            "🎮 Играть в 'Выживи до зарплаты'", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 Добро пожаловать в игру 'Выживи до зарплаты'!\n\n"
        "💼 Твоя задача - дожить до зарплаты, работая и избегая лишних трат.\n"
        "⚡ Работай, чтобы заработать деньги, но следи за энергией!\n"
        "📅 Каждый день приносит новые вызовы и случайные события.\n\n"
        "Нажми кнопку ниже, чтобы начать игру:",
        reply_markup=reply_markup
    )

def main():
    """Запуск бота"""
    if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
        print("❌ Ошибка: Установите TELEGRAM_BOT_TOKEN в файле .env")
        print("Получите токен у @BotFather в Telegram")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    
    print("🤖 Бот запущен!")
    print(f"🌐 Web App URL: {WEBAPP_URL}")
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()