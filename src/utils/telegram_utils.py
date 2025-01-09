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
        try:
            # Send message to the current chat_id
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
            # Debugging message indicating success
            print(f"Message sent successfully to chat_id: {chat_id}")
        except Exception as e:
            # Skip and log an error message for debugging purposes
            print(f"Failed to send message to chat_id: {chat_id}. Error: {e}")

def escape_markdown(text):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text
