import pytz
from datetime import datetime

IST = pytz.timezone("Asia/Kolkata")


def get_ist_datetime():
    return datetime.now(IST)


def get_ist_date():
    return get_ist_datetime().date()