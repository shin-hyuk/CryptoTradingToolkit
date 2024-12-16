import telegram
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")

# Initialize Telegram bot
bot = telegram.Bot(token=BOT_TOKEN)

async def send_message(message, parse_mode="Markdown"):
    """
    Send a message to multiple Telegram chat IDs.

    :param message: The message text to send.
    :param parse_mode: The format of the message (Markdown or HTML).
    """
    for chat_id in CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
            print(f"Message sent to chat ID {chat_id} successfully!")
        except telegram.error.TelegramError as e:
            print(f"Error sending message to chat ID {chat_id}: {e}")

def escape_markdown(text):
    """
    Escape special characters for Telegram Markdown formatting.

    :param text: The text to escape.
    :return: Escaped text.
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text
