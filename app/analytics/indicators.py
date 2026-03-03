import pandas as pd
import numpy as np

from app.analytics.momentum import add_momentum_features
from app.analytics.volatility import add_volatility_features


# -------------------------------------------------
# Moving Averages
# -------------------------------------------------
def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["ma20"] = df["Close"].rolling(window=20).mean()
    df["ma50"] = df["Close"].rolling(window=50).mean()
    return df


# -------------------------------------------------
# Volume
# -------------------------------------------------
def calculate_volume_ratio(df: pd.DataFrame) -> pd.DataFrame:
    df["avg_volume_20"] = df["Volume"].rolling(20).mean()
    df["volume_ratio"] = df["Volume"] / df["avg_volume_20"]
    return df


# -------------------------------------------------
# RSI
# -------------------------------------------------
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df


# -------------------------------------------------
# Apply All Indicators
# -------------------------------------------------
def apply_all_indicators(df: pd.DataFrame) -> pd.DataFrame:

    df = calculate_moving_averages(df)
    df = add_momentum_features(df)
    df = add_volatility_features(df)
    df = calculate_volume_ratio(df)
    df = calculate_rsi(df)

    return df