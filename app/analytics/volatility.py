import pandas as pd
import numpy as np


def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds rolling volatility and regime classification base.
    """

    df["volatility"] = (
        df["Close"].pct_change().rolling(20).std() * np.sqrt(252)
    )

    # Volatility percentile over 90 days
    if len(df) >= 30:
        df["volatility_percentile"] = (
            df["volatility"]
            .rolling(90)
            .apply(lambda x: (x < x.iloc[-1]).mean() * 100, raw=False)
        )
    else:
        df["volatility_percentile"] = None

    return df