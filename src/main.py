import btc
import crypto
import trade
import asyncio
from utils.telegram_utils import send_message

async def main():
    #trade.test_holdings("2020-01-01") #covid crash
    trade.test_5th_9th()
    
    #print("Starting workflows...")
    #msg = btc.get_whales()
    #msg += "\n\n" + crypto.get_trends()
    #await send_message(msg)
    #print("All workflows completed.")

if __name__ == "__main__":
    asyncio.run(main())
