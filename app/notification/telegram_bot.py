import os
import requests
from app.utils.logger import get_logger

logger = get_logger()

MAX_LENGTH = 4000


def send_telegram_message(message: str):

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    logger.info(f"Telegram token exists: {bool(bot_token)}")
    logger.info(f"Telegram chat id exists: {bool(chat_id)}")

    if not bot_token or not chat_id:
        logger.error("Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    chunks = [
        message[i:i + MAX_LENGTH]
        for i in range(0, len(message), MAX_LENGTH)
    ]

    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk
        }

        try:
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                logger.info("Telegram message sent successfully.")
            else:
                logger.error(
                    f"Telegram API error: {response.status_code} | {response.text}"
                )

        except Exception as e:
            logger.error(f"Telegram exception: {e}", exc_info=True)