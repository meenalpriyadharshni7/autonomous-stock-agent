from datetime import timedelta
from sqlalchemy import select, and_

from app.memory.models import Signal, DailyMetrics, SignalPerformance


class AccuracyTracker:

    def __init__(self, db_session):
        self.db = db_session

    # ---------------------------------------------------------
    # Evaluate 5-day forward performance
    # ---------------------------------------------------------
    def evaluate_signals(self, today):

        evaluation_date = today - timedelta(days=5)

        signals_to_check = self.db.execute(
            select(Signal).where(Signal.date == evaluation_date)
        ).scalars().all()

        for signal_record in signals_to_check:

            symbol = signal_record.stock_symbol
            signal_type = signal_record.signal

            # Prevent duplicate evaluation
            existing_eval = self.db.execute(
                select(SignalPerformance).where(
                    and_(
                        SignalPerformance.stock_symbol == symbol,
                        SignalPerformance.signal_date == evaluation_date
                    )
                )
            ).scalars().first()

            if existing_eval:
                continue

            entry_data = self.db.execute(
                select(DailyMetrics).where(
                    and_(
                        DailyMetrics.stock_symbol == symbol,
                        DailyMetrics.date == evaluation_date
                    )
                )
            ).scalars().first()

            exit_data = self.db.execute(
                select(DailyMetrics).where(
                    and_(
                        DailyMetrics.stock_symbol == symbol,
                        DailyMetrics.date == today
                    )
                )
            ).scalars().first()

            if not entry_data or not exit_data:
                continue

            entry_price = entry_data.close_price
            exit_price = exit_data.close_price

            if entry_price is None or exit_price is None:
                continue

            return_pct = ((exit_price - entry_price) / entry_price) * 100

            correct = False

            if signal_type == "BUY" and return_pct > 0:
                correct = True
            elif signal_type in ["DONT_BUY", "AVOID"] and return_pct < 0:
                correct = True

            performance_entry = SignalPerformance(
                stock_symbol=symbol,
                signal_date=evaluation_date,
                evaluation_date=today,
                signal_type=signal_type,
                entry_price=entry_price,
                exit_price=exit_price,
                return_after_5d=return_pct,
                correct_prediction=correct
            )

            self.db.add(performance_entry)

        self.db.commit()

    # ---------------------------------------------------------
    # Institutional Rolling Accuracy (365 Days)
    # ---------------------------------------------------------
    def compute_rolling_accuracy(self, lookback_days=365):

        # Get latest evaluation date in DB
        latest_record = self.db.execute(
            select(SignalPerformance)
            .order_by(SignalPerformance.evaluation_date.desc())
        ).scalars().first()

        if not latest_record:
            return 0.0

        cutoff_date = latest_record.evaluation_date - timedelta(days=lookback_days)

        performances = self.db.execute(
            select(SignalPerformance)
            .where(SignalPerformance.evaluation_date >= cutoff_date)
        ).scalars().all()

        if not performances:
            return 0.0

        total = len(performances)
        correct = sum(1 for p in performances if p.correct_prediction)

        accuracy = (correct / total) * 100

        return round(accuracy, 2)