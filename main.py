# main.py
import os
import asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables!")

# --- FLASK APP & TELEGRAM BOT SETUP ---
app = Flask(__name__)
ptb_app = Application.builder().token(TOKEN).build()

# --- BOT HANDLERS (Your bot's features) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(f"Hi {update.effective_user.mention_html()}! I am running on Render!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot is running 24/7 on a professional server.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("help", help_command))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- FLASK ROUTES ---
@app.route("/")
def index():
    # This is for health checks. Render will ping this to see if the bot is alive.
    return "OK"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    if request.is_json:
        update_data = request.get_json()
        update = Update.de_json(update_data, ptb_app.bot)
        await ptb_app.process_update(update)
        return Response("ok", status=200)
    return Response("bad request", status=400)


# This part is crucial for Render to run the app with Gunicorn
if __name__ == '__main__':
    # Initialize the bot application once
    asyncio.run(ptb_app.initialize())