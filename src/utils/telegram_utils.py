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
    for chat_id in CHAT_IDS:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)

def escape_markdown(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text
