import os
import requests
from dotenv import load_dotenv

from app.utils.logger import get_logger

load_dotenv()

logger = get_logger()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_LENGTH = 4000


def send_telegram_message(message: str):

    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    chunks = [
        message[i:i + MAX_LENGTH]
        for i in range(0, len(message), MAX_LENGTH)
    ]

    for chunk in chunks:

        payload = {
            "chat_id": CHAT_ID,
            "text": chunk
        }

        try:
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code != 200:
                logger.error(
                    f"Telegram API error: {response.status_code} | {response.text}"
                )
            else:
                logger.info("Telegram message sent successfully.")

        except Exception as e:
            logger.error(f"Telegram exception: {e}", exc_info=True)