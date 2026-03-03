import pandas as pd
from datetime import timedelta

from app.analytics.indicators import apply_all_indicators
from app.analytics.scoring import compute_score
from app.decision.signal_engine import classify_signal
from app.memory.models import SignalPerformance
from app.utils.logger import get_logger

logger = get_logger()


def backfill_accuracy(db, stock_data_dict, market_regime, holding_period=5):

    logger.info("Running historical accuracy backfill...")

    inserted = 0

    try:
        for symbol, df in stock_data_dict.items():

            if len(df) < holding_period + 50:
                logger.debug(f"{symbol}: Skipped (insufficient data for backfill).")
                continue

            df = df.copy()
            df = apply_all_indicators(df)
            df["score"] = df.apply(compute_score, axis=1)

            # Ensure datetime index
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            for i in range(50, len(df) - holding_period):

                row = df.iloc[i]
                enhanced_score = float(row.get("score", 0))

                signal, _, _ = classify_signal(
                    row,
                    enhanced_score,
                    market_regime,
                    breadth=50  # neutral baseline
                )

                # Only evaluate BUY-type signals
                if signal not in ["BUY", "STRONG_BUY"]:
                    continue

                entry_price = float(row["Close"])
                exit_price = float(df.iloc[i + holding_period]["Close"])

                return_pct = (exit_price - entry_price) / entry_price
                is_correct = return_pct > 0

                signal_date = df.index[i].date()
                evaluation_date = df.index[i + holding_period].date()

                # Prevent duplicate insert
                existing = db.query(SignalPerformance).filter(
                    SignalPerformance.stock_symbol == symbol,
                    SignalPerformance.signal_date == signal_date
                ).first()

                if existing:
                    continue

                performance = SignalPerformance(
                    stock_symbol=symbol,
                    signal_date=signal_date,
                    evaluation_date=evaluation_date,
                    signal_type=signal,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    return_after_5d=float(return_pct),
                    correct_prediction=is_correct
                )

                db.add(performance)
                inserted += 1

        db.commit()

        logger.info(f"Backfill completed successfully. Inserted {inserted} records.")

    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        db.rollback()