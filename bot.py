import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# --- CONFIG ---
TOKEN = "8697037269:AAE0EBm0pYVxSb3x916yT-hsv6Cjogaac18"
GEMINI_KEY = "AIzaSyBscsRuuxToNnENbzBm1OOPE-hrGTbk3FM"
OWNER_ID = 8732201707 

# Memory (Users aur Groups ko yaad rakhne ke liye)
all_chats = set() 
current_status = "Sandeep bhai abhi offline hain."

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- HEALTH SERVER ---
class HealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sandeep's Boss Bot is 100% Loaded!")

# --- MASTER FUNCTIONS ---

# 1. Welcome & Chat Tracker (Bot ko sab yaad rahega)
async def track_and_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_chats.add(update.effective_chat.id)
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"Ram Ram {member.full_name}! 🙏\nSandeep bhai ke group mein swagat hai. Tamiz se rehna!")

# 2. Kick/Ban Command (Nikalne ke liye)
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"✈️ {user.full_name} ko nikal diya gaya!")

# 3. Mute Command (Bolti band)
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        permissions = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions)
        await update.message.reply_text(f"🤫 {user.full_name} ki bolti band kar di gayi hai!")

# 4. Main Controller (AI, Forwarding, Broadcast)
async def handle_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_status
    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    all_chats.add(chat_id) # Save chat ID

    # --- OWNER POWERS ---
    if user.id == OWNER_ID:
        # Broadcast to ALL (Groups + DMs)
        if text.lower().startswith("bhejdo:"):
            msg = text[7:].strip()
            for cid in list(all_chats):
                try: await context.bot.send_message(chat_id=cid, text=msg)
                except: pass
            await update.message.reply_text("✅ Sabhi groups aur personal chats mein message bhej diya!")
            return

        # Status Update
        if text.lower().startswith("update:"):
            current_status = text[7:].strip()
            await update.message.reply_text(f"✅ Naya Status: {current_status}")
            return

    # --- USER SECTION ---
    if update.message.chat.type == 'private':
        # 1. Forward to Sandeep
        await context.bot.send_message(OWNER_ID, f"📩 **Message Aaya Hai!**\n👤 {user.full_name}\n💬 {text}")
        
        # 2. AI Smart Reply
        prompt = f"Tum Sandeep ke manager ho. Sandeep ka status: {current_status}. User ({user.full_name}) ne kaha: {text}. Friendly Hinglish mein reply do."
        try:
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text)
        except:
            await update.message.reply_text("Sandeep bhai busy hain.")

# --- RUN BOT ---
if __name__ == '__main__':
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8000), HealthServer).serve_forever(), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("nikal", kick_user)) # Kisi ke reply pe /nikal likho
    app.add_handler(CommandHandler("chup", mute_user))   # Kisi ke reply pe /chup likho
    
    # Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_and_welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_main))
    
    print("🚀 Master Bot is ONLINE!")
    app.run_polling()

