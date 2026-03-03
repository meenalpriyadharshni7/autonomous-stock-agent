import pandas as pd
import numpy as np


def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds multi-horizon momentum features.
    """

    df["momentum_7d"] = df["Close"].pct_change(7) * 100
    df["momentum_30d"] = df["Close"].pct_change(30) * 100

    # Momentum slope (acceleration proxy)
    df["momentum_slope"] = df["momentum_7d"].diff()

    return df