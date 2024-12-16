from utils import telegram_utils as telegram
from .get_google_trends import get_google_trends
from .get_greed_fear_index import get_greed_fear_index

async def send_trends():
    msg = get_google_trends()
    msg += "\n" + get_greed_fear_index()
    await telegram.send_message(msg)