from utils import telegram_utils as telegram
from .get_distribution import get_distribution
from .get_chain import get_chain

def get_whales():
    msg = get_distribution()
    msg += "\n\n" + get_chain()
    return msg