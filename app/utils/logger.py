import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name="ai_agent"):

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # Prevent duplicate handlers

    os.makedirs("logs", exist_ok=True)

    # -------------------------------
    # Formatter
    # -------------------------------
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # -------------------------------
    # Console Handler
    # -------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # -------------------------------
    # Rotating File Handler (All Logs)
    # -------------------------------
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # -------------------------------
    # Error File Handler
    # -------------------------------
    error_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger