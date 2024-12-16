import btc
import crypto
import asyncio

async def main():
    """
    Main entry point to orchestrate all workflows.
    """
    print("Starting workflows...")
    await btc.send_distribution()
    await btc.send_chain()
    await crypto.send_trends()
    print("All workflows completed.")

if __name__ == "__main__":
    asyncio.run(main())
