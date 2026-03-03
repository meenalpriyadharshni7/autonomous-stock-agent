import numpy as np


def normalize(value, min_val, max_val):
    if max_val - min_val == 0:
        return 50
    return 100 * (value - min_val) / (max_val - min_val)


def compute_score(
    row,
    market_regime=None,
    momentum_min=-20,
    momentum_max=20
):
    """
    Regime-Adaptive Weighted Scoring Model (0–100 bounded)
    """

    # --------------------------------------------------
    # Default (Neutral) Weights
    # --------------------------------------------------
    momentum_w = 0.30
    trend_w = 0.25
    volume_w = 0.15
    rsi_w = 0.15
    volatility_w = 0.15

    # --------------------------------------------------
    # Regime Adaptation
    # --------------------------------------------------
    if market_regime:

        trend = market_regime.get("trend")
        volatility_state = market_regime.get("volatility")

        # Bearish → defensive
        if trend == "bearish":
            momentum_w = 0.15
            trend_w = 0.20
            volume_w = 0.10
            rsi_w = 0.20
            volatility_w = 0.35

        # Bullish → aggressive
        elif trend == "bullish":
            momentum_w = 0.40
            trend_w = 0.30
            volume_w = 0.15
            rsi_w = 0.10
            volatility_w = 0.05

        # Extra penalty in high volatility
        if volatility_state == "high":
            volatility_w = min(volatility_w + 0.10, 0.40)

    # --------------------------------------------------
    # Feature Scores
    # --------------------------------------------------
    momentum_raw = row.get("momentum_7d", 0)
    momentum_score = normalize(momentum_raw, momentum_min, momentum_max)

    trend_score = (
        (row.get("Close", 0) > row.get("ma20", 0)) * 0.5 +
        (row.get("Close", 0) > row.get("ma50", 0)) * 0.5
    ) * 100

    volume_score = min(row.get("volume_ratio", 1) * 40, 100)

    rsi = row.get("rsi", 50)
    rsi_distance = abs(rsi - 57)
    rsi_score = max(0, 100 - rsi_distance * 2)

    volatility_penalty = min(row.get("volatility", 0) * 30, 100)

    # --------------------------------------------------
    # Final Score
    # --------------------------------------------------
    final_score = (
        momentum_w * momentum_score +
        trend_w * trend_score +
        volume_w * volume_score +
        rsi_w * rsi_score -
        volatility_w * volatility_penalty
    )

    final_score = max(0, min(100, final_score))

    return final_score