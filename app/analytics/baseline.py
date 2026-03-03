import pandas as pd
import numpy as np


class HistoricalBaselineEngine:
    def __init__(self, window: int = 90):
        self.window = window

    def compute_relative_metrics(self, df: pd.DataFrame) -> dict:
        """
        Takes 90-day enriched dataframe.
        Returns intelligence metrics for latest day.
        """

        if len(df) < 30:
            return {}

        latest = df.iloc[-1]
        last_7 = df.tail(7)
        last_30 = df.tail(30)
        last_90 = df.tail(self.window)

        metrics = {}

        # Score comparison (if you add score column later)
        if "score" in df.columns:
            metrics["score_vs_7d_avg"] = (
                latest["score"] - last_7["score"].mean()
            )
            metrics["score_vs_30d_avg"] = (
                latest["score"] - last_30["score"].mean()
            )

        # Momentum acceleration
        if "momentum_7d" in df.columns:
            avg_30_momentum = last_30["momentum_7d"].mean()
            if avg_30_momentum != 0:
                metrics["momentum_acceleration"] = (
                    latest["momentum_7d"] / avg_30_momentum
                )
            else:
                metrics["momentum_acceleration"] = 0

        # Volatility regime
        if "volatility" in df.columns:
            avg_vol_30 = last_30["volatility"].mean()
            if latest["volatility"] > avg_vol_30 * 1.2:
                metrics["volatility_regime"] = "expanding"
            elif latest["volatility"] < avg_vol_30 * 0.8:
                metrics["volatility_regime"] = "compressing"
            else:
                metrics["volatility_regime"] = "stable"

        # RSI percentile
        if "rsi" in df.columns:
            metrics["rsi_percentile_90d"] = (
                (last_90["rsi"] < latest["rsi"]).mean() * 100
            )

        # Price percentile
        min_price = last_90["Close"].min()
        max_price = last_90["Close"].max()
        if max_price != min_price:
            metrics["price_percentile_90d"] = (
                (latest["Close"] - min_price) /
                (max_price - min_price)
            ) * 100
        else:
            metrics["price_percentile_90d"] = 0

        # Volume expansion
        if "volume_ratio" in df.columns:
            metrics["volume_expansion_ratio"] = latest["volume_ratio"]

        return metrics