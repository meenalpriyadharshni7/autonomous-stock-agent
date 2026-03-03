from sqlalchemy import select, desc
from app.memory.models import DailyMetrics, Signal


# =====================================================
# DAILY METRICS REPOSITORY
# =====================================================
class DailyMetricsRepository:

    def __init__(self, db):
        self.db = db

    # -------------------------------------------
    # Add new metrics
    # -------------------------------------------
    def add(self, metrics: DailyMetrics):
        self.db.add(metrics)

    # -------------------------------------------
    # Check if metrics already exist for date
    # -------------------------------------------
    def exists_for_date(self, date) -> bool:
        return self.db.execute(
            select(DailyMetrics)
            .where(DailyMetrics.date == date)
        ).first() is not None

    # -------------------------------------------
    # Get latest previous record for stock
    # -------------------------------------------
    def get_latest_before_date(self, symbol: str, date):
        return self.db.execute(
            select(DailyMetrics)
            .where(DailyMetrics.stock_symbol == symbol)
            .where(DailyMetrics.date < date)
            .order_by(desc(DailyMetrics.date))
        ).scalars().first()

    # -------------------------------------------
    # Get metrics for specific date
    # -------------------------------------------
    def get_by_date(self, date):
        return self.db.execute(
            select(DailyMetrics)
            .where(DailyMetrics.date == date)
        ).scalars().all()


# =====================================================
# SIGNAL REPOSITORY
# =====================================================
class SignalRepository:

    def __init__(self, db):
        self.db = db

    # -------------------------------------------
    # Add new signal
    # -------------------------------------------
    def add(self, signal: Signal):
        self.db.add(signal)

    # -------------------------------------------
    # Get latest previous signal for stock
    # -------------------------------------------
    def get_latest_before_date(self, symbol: str, date):
        return self.db.execute(
            select(Signal)
            .where(Signal.stock_symbol == symbol)
            .where(Signal.date < date)
            .order_by(desc(Signal.date))
        ).scalars().first()

    # -------------------------------------------
    # Get signals for specific date
    # -------------------------------------------
    def get_by_date(self, date):
        return self.db.execute(
            select(Signal)
            .where(Signal.date == date)
        ).scalars().all()

    # -------------------------------------------
    # Get all signals
    # -------------------------------------------
    def get_all(self):
        return self.db.execute(
            select(Signal)
        ).scalars().all()