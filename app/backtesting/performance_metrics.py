import numpy as np
from sqlalchemy import select, desc
from app.memory.models import SignalPerformance


class PerformanceMetrics:

    def __init__(self, db):
        self.db = db

    def compute_metrics(self, window: int = 60):
        """
        Computes rolling performance metrics using last N evaluated signals.
        """

        records = self.db.execute(
            select(SignalPerformance)
            .order_by(desc(SignalPerformance.evaluation_date))
            .limit(window)
        ).scalars().all()

        if not records:
            return self._empty_metrics()

        # Extract valid non-zero returns
        returns = [
            r.return_after_5d
            for r in records
            if r.return_after_5d is not None and r.return_after_5d != 0
        ]

        if not returns:
            return self._empty_metrics()

        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]

        total = len(returns)

        hit_rate = (len(wins) / total) * 100 if total > 0 else 0
        avg_return = float(np.mean(returns))

        avg_win = float(np.mean(wins)) if wins else 0
        avg_loss = abs(float(np.mean(losses))) if losses else 0

        win_loss_ratio = (avg_win / avg_loss) if avg_loss != 0 else 0

        # Proper expectancy calculation
        win_prob = len(wins) / total if total > 0 else 0
        loss_prob = 1 - win_prob

        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

        return {
            "hit_rate": round(hit_rate, 2),
            "avg_return": round(avg_return, 4),
            "win_loss_ratio": round(win_loss_ratio, 4),
            "expectancy": round(expectancy, 4)
        }

    def _empty_metrics(self):
        return {
            "hit_rate": 0.0,
            "avg_return": 0.0,
            "win_loss_ratio": 0.0,
            "expectancy": 0.0
        }