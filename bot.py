import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# --- DUMMY SERVER (Hosting par bot ko zinda rakhne ke liye) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    server.serve_forever()

# ================= CONFIG (Don't Change These) =================
BOT_TOKEN = "8697037269:AAEvJfIsm8HB7xikCeG-vkrBDcRDtBjgY70"
GEMINI_API_KEY = "AIzaSyBF8GrgZN_dZThwXvwirKxBLzMGfCiZmtY" 

OWNER_ID = 8732201707
MAIN_GROUP = -1003886374834
MOVIE_GROUP = -1003943718007

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def ai_reply(user_text):
    try:
        response = model.generate_content(f"Friendly reply in Hinglish: {user_text}")
        return response.text.strip()
    except: 
        return "⚠️ Thoda ruko bhai, server busy hai."

# ================= MAIN HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    if chat_id != MAIN_GROUP: return

    text = update.message.text
    user = update.effective_user

    # Movie keywords check
    if any(kw in text.lower() for kw in ["movie", "chahiye", "dedo", "link", "film"]):
        msg = f"🎬 **NEW MOVIE REQUEST**\n\n👤 **User:** {user.full_name}\n🆔 **ID:** `{user.id}`\n💬 **Msg:** {text}"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode='Markdown')
        await context.bot.send_message(chat_id=MOVIE_GROUP, text=msg, parse_mode='Markdown')
        await update.message.reply_text("✅ Request forward kar di gayi hai!")
        return

    # AI Chat
    reply = ai_reply(text)
    await update.message.reply_text(reply)

# ================= RUN BOT =================
if __name__ == '__main__':
    # Start Dummy Server for Koyeb
    threading.Thread(target=run_health_server, daemon=True).start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    
    print("🚀 Bot is starting on Cloud...")
    app.run_polling(drop_pending_updates=True)

