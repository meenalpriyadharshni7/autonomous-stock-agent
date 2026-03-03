def adjust_confidence(
    base_confidence,
    rolling_accuracy,
    market_regime,
    expectancy,
    breadth
):
    """
    Adaptive confidence scaling based on:
    - Historical accuracy
    - Strategy expectancy
    - Market regime
    - Market breadth (participation strength)
    """

    confidence = base_confidence

    # -----------------------------------------
    # 1️⃣ Accuracy Scaling
    # -----------------------------------------
    if rolling_accuracy < 50:
        confidence *= 0.85
    elif rolling_accuracy > 65:
        confidence *= 1.10

    # -----------------------------------------
    # 2️⃣ Expectancy Scaling
    # -----------------------------------------
    if expectancy > 1:
        confidence *= 1.10
    elif expectancy < 0:
        confidence *= 0.85

    # -----------------------------------------
    # 3️⃣ Market Regime Scaling
    # -----------------------------------------
    trend = market_regime.get("trend")
    volatility = market_regime.get("volatility")

    if trend == "bearish":
        confidence *= 0.90

    if volatility == "high":
        confidence *= 0.90

    # -----------------------------------------
    # 4️⃣ Market Breadth Scaling (NEW)
    # -----------------------------------------
    if breadth > 0.65:
        confidence *= 1.05
    elif breadth < 0.40:
        confidence *= 0.90

    # Bound between 40% and 95%
    confidence = max(40, min(95, confidence))

    return round(confidence, 2)