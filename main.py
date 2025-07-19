# main.py
import os
import asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from hypercorn.config import Config
from hypercorn.asyncio import serve
import uvloop

# --- CONFIGURATION ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Railway provides the PORT it wants the server to run on.
PORT = int(os.environ.get('PORT', 8080))

# --- VALIDATION ---
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables!")

# --- FLASK APP & TELEGRAM BOT SETUP ---
app = Flask(__name__)
ptb_app = Application.builder().token(TOKEN).build()

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(f"Hi {update.effective_user.mention_html()}! I am running correctly now!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot should now respond to every message.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("help", help_command))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# --- FLASK ROUTES ---
@app.route("/")
def index():
    # A simple page for UptimeRobot to ping
    return "OK"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    if request.is_json:
        update_data = request.get_json()
        update = Update.de_json(update_data, ptb_app.bot)
        await ptb_app.process_update(update)
        return Response("ok", status=200)
    return Response("bad request", status=400)


# --- MAIN ASYNC FUNCTION TO RUN EVERYTHING ---
async def main():
    """This function controls the entire lifecycle of the bot."""
    
    # We get the public URL from Railway's environment variables.
    # This is only available after the initial deployment.
    railway_url = os.environ.get('RAILWAY_STATIC_URL')
    if not railway_url:
        print("Could not find RAILWAY_STATIC_URL. This is normal on first deploy.")
        print("The webhook will be set on the next deploy after the URL is available.")
    else:
        # The URL needs to start with https://
        webhook_url = f"https://{railway_url}/{TOKEN}"
        await ptb_app.initialize()
        print(f"Setting webhook to: {webhook_url}")
        await ptb_app.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
        print("Webhook set successfully!")

    # Configure Hypercorn to run the Flask app
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    config.worker_class = "uvloop"

    print(f"Starting Hypercorn server on port {PORT}...")
    # Run the server
    await serve(app, config)


if __name__ == "__main__":
    # Install the uvloop event loop policy for better performance
    uvloop.install()
    # Run the main async function
    asyncio.run(main())
