from sqlalchemy import select
from app.memory.models import Signal


class SignalEvaluator:

    def __init__(self, db_session):
        self.db = db_session

    def get_evaluated_signals(self):

        signals = self.db.execute(
            select(Signal).where(Signal.outcome != None)
        ).scalars().all()

        return signals