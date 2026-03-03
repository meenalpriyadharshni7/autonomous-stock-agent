import numpy as np
import pandas as pd

from app.data.fetcher import fetch_stock_data
from app.analytics.indicators import apply_all_indicators


class MarketRegimeEngine:
    def __init__(self, symbol="^NSEI"):
        self.symbol = symbol

    def detect_regime(self):

        df = fetch_stock_data(self.symbol)

        if df is None or len(df) < 50:
            return {
                "trend": "unknown",
                "volatility": "unknown",
                "momentum": 0.0
            }

        df = apply_all_indicators(df)

        latest = df.iloc[-1]

        # ----------------------------
        # Trend Detection
        # ----------------------------
        close_price = float(latest["Close"])
        ma50 = float(latest["ma50"])

        if close_price > ma50:
            trend = "bullish"
        elif close_price < ma50:
            trend = "bearish"
        else:
            trend = "sideways"

        # ----------------------------
        # Volatility Regime
        # ----------------------------
        vol_mean = float(df["volatility"].tail(30).mean())
        latest_vol = float(latest["volatility"])

        if latest_vol > vol_mean * 1.2:
            volatility = "high"
        elif latest_vol < vol_mean * 0.8:
            volatility = "low"
        else:
            volatility = "normal"

        # ----------------------------
        # Momentum (Sanitized)
        # ----------------------------
        momentum_raw = latest.get("momentum_30d", 0)

        # Handle numpy types and NaN safely
        if pd.isna(momentum_raw):
            momentum = 0.0
        else:
            momentum = float(momentum_raw)

        return {
            "trend": str(trend),
            "volatility": str(volatility),
            "momentum": momentum
        }