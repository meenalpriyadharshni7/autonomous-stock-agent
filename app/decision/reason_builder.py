def build_reason_narrative(row, signal, market_regime, breadth):
    """
    Generates detailed explanation for signal.
    """

    reasons = []

    # Structural context
    if row.get("rsi", 50) > 65:
        reasons.append("RSI elevated — strong momentum")
    elif row.get("rsi", 50) < 40:
        reasons.append("RSI weak — bearish pressure")

    if row.get("momentum_7d", 0) > 0:
        reasons.append("Short-term momentum positive")

    if row.get("momentum_acceleration", 1) > 1.2:
        reasons.append("Momentum accelerating")

    # Market context
    if market_regime.get("trend") == "bearish":
        reasons.append("Overall market bearish — risk adjusted")

    if breadth < 40:
        reasons.append("Weak market breadth")

    if not reasons:
        reasons.append("Mixed indicators")

    return reasons