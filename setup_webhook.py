import asyncio

import aiohttp

from config import CRYPTOBOT_API_URL, CRYPTOBOT_TOKEN


async def setup_cryptobot_webhook(webhook_url: str):
    """
    Register CryptoBot webhook URL.
    Example: https://your-app.railway.app/webhook/cryptobot
    """
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            f"{CRYPTOBOT_API_URL}/setWebhook",
            headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
            json={"url": webhook_url},
        )
        data = await response.json()
        print(f"Webhook setup result: {data}")
        return data


if __name__ == "__main__":
    webhook_url = "https://your-app.railway.app/webhook/cryptobot"
    asyncio.run(setup_cryptobot_webhook(webhook_url))
