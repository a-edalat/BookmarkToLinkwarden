import os
import re
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# https://docs.linkwarden.app/api/create-link

# Manually load .env file
with open(".env") as f:
    for line in f:
        try:
            key, value = line.strip().split("=", 1)
        except ValueError:
            continue
        os.environ[key] = value  # Set each key-value pair in the environment

# Retrieve token/URL values
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LINKWARDEN_API_URL = os.getenv("LINKWARDEN_API_URL")
LINKWARDEN_API_KEY = os.getenv("LINKWARDEN_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

# Regex pattern to extract URLs
URL_PATTERN = re.compile(r'https?://\S+')

def extract_links(text):
    """Extract URLs from a given text."""
    return URL_PATTERN.findall(text)

async def send_to_linkwarden(url):
    """Send the extracted URL to Linkwarden."""
    headers = {"Authorization": f"Bearer {LINKWARDEN_API_KEY}", "Content-Type": "application/json"}
    payload = {"url": url, "title": "Auto-saved Bookmark"}  # Customize if needed

    response = requests.post(LINKWARDEN_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"Successfully saved: {url}")
    else:
        print(f"Failed to save {url}: {response.text}")

async def handle_message(update: Update, context: CallbackContext):
    """Handle incoming messages and extract URLs."""
    if update.message and str(update.message.chat_id) == CHAT_ID:
        text = update.message.text
        urls = extract_links(text)

        for url in urls:
            await send_to_linkwarden(url)
            await context.bot.send_message(chat_id=CHAT_ID, text=f"Successfully saved: {url}")

def main():
    """Start the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is listening for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()