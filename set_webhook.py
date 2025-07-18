# set_webhook.py
import os
import asyncio
import sys
from telegram import Bot

async def main():
    """A simple script to set the webhook."""
    if len(sys.argv) != 3:
        print("Usage: python set_webhook.py <YOUR_BOT_TOKEN> <YOUR_RAILWAY_URL>")
        sys.exit(1)

    token = sys.argv[1]
    railway_url = sys.argv[2]
    webhook_url = f"{railway_url.rstrip('/')}/{token}"

    bot = Bot(token=token)
    print(f"Setting webhook to: {webhook_url}")
    if await bot.set_webhook(url=webhook_url):
        print("Webhook set successfully!")
    else:
        print("Error setting webhook.")

if __name__ == "__main__":
    asyncio.run(main())
