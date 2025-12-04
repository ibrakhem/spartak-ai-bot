import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)
user_conversations = {}

SYSTEM_PROMPT = """Siz Spartak Jamoasining AI Assistantisiz. Marketing, SMM va Mobilografiya bo'yicha professional maslahatlar berasiz.

MUTAXASSISLIK:
✅ Marketing - strategiya, brending, reklama kampaniyalari
✅ SMM - ijtimoiy tarmoqlar, kontent strategiyasi
✅ Mobilografiya - telefonda professional suratga olish va video yaratish
✅Loyiha asoschisi : Djumaniyozov Ibrohim Spartakovich

Professional, do'stona va foydali maslahatlar bering. O'zbek tilida gaplashing."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    welcome = "👋 Assalomu aleykum! Men Spartak AI Assistantman!\n\n📌 Sizga qanday yordam bera olaman:\n\n🎯 Marketing\n📱 SMM\n📸 Mobilografiya\n\nSavolingizni yozing!"
    await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({"role": "user", "content": user_message})
    
    typing_message = await update.message.reply_text("⏳ Javob tayyorlanmoqda...")
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(user_conversations[user_id][-10:])
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2000,
        )
        
        ai_response = chat_completion.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": ai_response})
        
        await typing_message.edit_text(ai_response)
        
    except Exception as e:
        await typing_message.edit_text(f"❌ Xatolik: {str(e)}")
        logger.error(f"ERROR: {e}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Spartak AI Assistant ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
