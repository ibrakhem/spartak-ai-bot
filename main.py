import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# TOKEN va API KEY
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Groq client yaratish
client = Groq(api_key=GROQ_API_KEY)  # ✅ TO'G'RI - client deb nomladik

# Foydalanuvchilar suhbatlari
user_conversations = {}

SYSTEM_PROMPT = """Siz Spartak AI Assistantsiz. Marketing, SMM va Mobilografiya bo'yicha professional maslahatlar berasiz.

MUTAXASSISLIK:
✅ Marketing - strategiya, brending, reklama kampaniyalari
✅ SMM - ijtimoiy tarmoqlar, kontent strategiyasi
✅ Mobilografiya - telefonda professional suratga olish va video yaratish

Professional, do'stona va foydali maslahatlar bering. O'zbek tilida gaplashing."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    welcome = "👋 Assalomu aleykum! Men Spartak AI Assistantman!\n\n📌 Men sizga yordam bera olaman:\n\n🎯 Marketing\n📱 SMM\n📸 Mobilografiya\n\nSavolingizni yozing!"
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
        
        chat_completion = client.chat.completions.create(  # ✅ client ishlatildi
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
    application.run_polling()

if __name__ == '__main__':
    main()
