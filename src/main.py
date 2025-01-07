import btc
import crypto
import asyncio
from utils.telegram_utils import send_message

async def main():
    """
    Main entry point to orchestrate all workflows.
    """
    print("Starting workflows...")
    msg = btc.get_whales()
    msg += "\n\n" + crypto.get_trends()
    await send_message(msg)
    print("All workflows completed.")

if __name__ == "__main__":
    asyncio.run(main())
