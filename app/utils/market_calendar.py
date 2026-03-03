import pandas_market_calendars as mcal
from app.utils.time_utils import get_ist_date
from app.utils.logger import get_logger

logger = get_logger()


def is_nse_trading_day():
    """
    Returns True only if today is a valid NSE trading day.
    Safely handles weekends and calendar exceptions.
    """

    try:
        today = get_ist_date()

        # Weekend guard
        if today.weekday() >= 5:
            logger.info(f"{today} is weekend. NSE closed.")
            return False

        nse = mcal.get_calendar("NSE")

        schedule = nse.schedule(
            start_date=today,
            end_date=today
        )

        if schedule.empty:
            logger.info(f"{today} is NSE holiday. Market closed.")
            return False

        logger.info(f"{today} is valid NSE trading day.")
        return True

    except Exception as e:
        logger.error(f"Market calendar check failed: {e}", exc_info=True)
        return False