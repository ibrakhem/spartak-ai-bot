import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Siz Spartak AI Assistantsiz. Marketing, SMM va mobilografiya bo'yicha professional maslahatchi."""

user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    welcome = "👋 Assalomu aleykum! Men Spartak AI Assistantman!\n\n📊 Marketing\n📱 SMM\n📸 Mobilografiya\n\nSavolingizni bering! 🚀"
    await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    typing_message = await update.message.reply_text("⏳ Javob tayyorlanmoqda...")
    
    try:
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_conversations[user_id]
        
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1500,
        )
        
        bot_response = chat_completion.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": bot_response})
        
        await typing_message.delete()
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await typing_message.delete()
        await update.message.reply_text("❌ Kechirasiz, xatolik yuz berdi.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
