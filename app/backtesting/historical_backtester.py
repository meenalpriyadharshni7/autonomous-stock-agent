import pandas as pd
import numpy as np
from app.analytics.indicators import apply_all_indicators
from app.analytics.scoring import compute_score
from app.decision.signal_engine import classify_signal


class HistoricalBacktester:

    def __init__(self, lookback_days=60, forward_days=5):
        self.lookback_days = lookback_days
        self.forward_days = forward_days

    def run_backtest(self, stock_data_dict, market_regime):

        results = []

        for symbol, df in stock_data_dict.items():

            df = df.copy()
            df = apply_all_indicators(df)
            df["score"] = df.apply(compute_score, axis=1)

            # Only simulate last N days
            for i in range(len(df) - self.forward_days - self.lookback_days,
                           len(df) - self.forward_days):

                historical_slice = df.iloc[:i+1]
                latest = historical_slice.iloc[-1]

                signal, confidence, _ = classify_signal(
                    latest,
                    latest["score"],
                    market_regime
                )

                entry_price = latest["Close"]
                exit_price = df.iloc[i + self.forward_days]["Close"]

                return_pct = ((exit_price - entry_price) / entry_price) * 100

                correct = False

                if signal == "BUY" and return_pct > 0:
                    correct = True

                if signal == "DONT_BUY" and return_pct < 0:
                    correct = True

                results.append({
                    "symbol": symbol,
                    "signal": signal,
                    "return": return_pct,
                    "correct": correct
                })

        return pd.DataFrame(results)


def summarize_backtest(results_df):

    if results_df.empty:
        return {}

    returns = results_df["return"].tolist()

    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r <= 0]

    hit_rate = len(wins) / len(returns) * 100
    avg_return = np.mean(returns)

    avg_win = np.mean(wins) if wins else 0
    avg_loss = abs(np.mean(losses)) if losses else 0

    expectancy = (hit_rate / 100 * avg_win) - (
        (1 - hit_rate / 100) * avg_loss
    )

    return {
        "total_trades": len(returns),
        "hit_rate": round(hit_rate, 2),
        "avg_return": round(avg_return, 2),
        "expectancy": round(expectancy, 2)
    }