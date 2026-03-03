import smtplib
from email.mime.text import MIMEText

from config import (
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    SMTP_SERVER,
    SMTP_PORT
)

from app.utils.logger import get_logger

logger = get_logger()


def send_email(subject, message):

    msg = MIMEText(message, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        logger.info("Email sent successfully.")

    except Exception as e:
        logger.error(f"Email sending failed: {e}", exc_info=True)