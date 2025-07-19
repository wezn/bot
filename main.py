# main.py
import os
import asyncio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables!")

# --- TELEGRAM BOT SETUP ---
ptb_app = Application.builder().token(TOKEN).build()

# A flag to ensure the bot is initialized only once.
_is_initialized = False

# --- BOT HANDLERS (Your bot's features) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(f"Hi {update.effective_user.mention_html()}! I am running correctly now!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot should now respond to every message.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("help", help_command))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# --- WEB SERVER ROUTES ---
async def health_check(request: Request):
    """A simple page for UptimeRobot to ping."""
    return PlainTextResponse("OK")

async def webhook(request: Request):
    """This function is called by Telegram."""
    global _is_initialized
    # Initialize the bot on the very first request.
    if not _is_initialized:
        await ptb_app.initialize()
        _is_initialized = True

    try:
        update_data = await request.json()
        update = Update.de_json(update_data, ptb_app.bot)
        await ptb_app.process_update(update)
        return Response(status_code=200)
    except Exception:
        return Response(status_code=400)

# Define the routes for our Starlette application
routes = [
    Route("/", endpoint=health_check),
    Route(f"/{TOKEN}", endpoint=webhook, methods=["POST"]),
]

# Create the Starlette application instance
# gunicorn will look for this 'app' object to run.
app = Starlette(routes=routes)
