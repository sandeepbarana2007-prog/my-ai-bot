import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8759801824:AAH9IYoOezLN7efvQqtHz_u9QtkpsaO2Unw"
GEMINI_KEY = "AIzaSyBscsRuuxToNnENbzBm1OOPE-hrGTbk3FM"
OWNER_ID = 8732201707  # Aapki confirm ID

# AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- RENDER HEALTH CHECK SERVER ---
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Rose AI is Running!")

def run_server():
    HTTPServer(('0.0.0.0', 8000), HealthServer).serve_forever()

# --- BOT COMMANDS (ROSE STYLE) ---

# Welcome Message
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Ram Ram {member.full_name}! 🙏\nGroup mein aapka swagat hai. Rules padhne ke liye /rules likhen.")

# Rules Command
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = (
        "📜 **Group Rules:**\n"
        "1. Kisi ko gaali na dein.\n"
        "2. Spamming mana hai.\n"
        "3. Sirf kaam ki baat karein.\n"
        "4. Admin ki baat maanein."
    )
    await update.message.reply_text(rules_text, parse_mode="Markdown")

# Ban Command (Reply to user)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 {user.full_name} ko ban kar diya gaya!")

# AI Chat & Personal Assistant
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    text = update.message.text
    
    # AI tabhi chalega jab DM ho ya bot ko tag kiya jaye
    if update.message.chat.type == 'private' or f"@{context.bot.username}" in text:
        prompt = f"Tum Sandeep Gurjar ke assistant ho. Friendly Hinglish mein jawab do. User ne kaha: {text}"
        try:
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text)
        except:
            await update.message.reply_text("Sandeep bhai abhi busy hain, baad mein try karein.")

# --- MAIN RUNNER ---
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    
    print("🚀 Rose AI Bot Started!")
    app.run_polling()

