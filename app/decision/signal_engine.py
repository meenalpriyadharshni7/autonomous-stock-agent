from app.decision.reason_builder import build_reason_narrative


def classify_signal(row, enhanced_score, market_regime, breadth):
    """
    Continuous tier-based signal classification.
    No hard BUY suppression.
    Designed for ranked allocation model.
    """

    acceleration = row.get("momentum_acceleration", 1)
    volatility_regime = row.get("volatility_regime", "stable")

    market_trend = market_regime.get("trend", "neutral")
    market_vol = market_regime.get("volatility", "normal")

    # -----------------------------------------------------
    # SIGNAL TIERS (Score Based)
    # -----------------------------------------------------
    if enhanced_score >= 70:
        signal = "STRONG_BUY"
        base_confidence = 80
    elif enhanced_score >= 60:
        signal = "BUY"
        base_confidence = 70
    elif enhanced_score >= 50:
        signal = "HOLD"
        base_confidence = 60
    else:
        signal = "AVOID"
        base_confidence = 40

    # -----------------------------------------------------
    # Acceleration Adjustment
    # -----------------------------------------------------
    base_confidence += (acceleration - 1) * 10

    # -----------------------------------------------------
    # Volatility Adjustment (not blocking)
    # -----------------------------------------------------
    if volatility_regime == "expanding":
        base_confidence -= 5

    # -----------------------------------------------------
    # Market Regime Scaling
    # -----------------------------------------------------
    if market_trend == "bearish":
        base_confidence *= 0.8
    elif market_trend == "bullish":
        base_confidence *= 1.05

    if market_vol == "high":
        base_confidence *= 0.9

    base_confidence = max(30, min(95, base_confidence))

    reasons = build_reason_narrative(
        row=row,
        signal=signal,
        market_regime=market_regime,
        breadth=breadth
    )

    return signal, round(base_confidence, 2), reasons