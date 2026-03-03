import pandas as pd


def rank_stocks(stock_data_dict):

    rankings = []

    for symbol, df in stock_data_dict.items():
        latest = df.iloc[-1]

        base_score = float(latest.get("score", 0))
        enhanced_score = base_score

        # ---------------------------------------
        # Acceleration Bonus
        # ---------------------------------------
        acceleration = latest.get("momentum_acceleration", 1)

        if acceleration > 1.5:
            enhanced_score += 5
        elif acceleration > 1.2:
            enhanced_score += 2

        # ---------------------------------------
        # Volatility Regime Adjustment
        # ---------------------------------------
        volatility_regime = latest.get("volatility_regime", "stable")

        if volatility_regime == "expanding":
            enhanced_score -= 5
        elif volatility_regime == "compressing":
            enhanced_score += 2

        # ---------------------------------------
        # Breakout Bonus
        # ---------------------------------------
        price_percentile = latest.get("price_percentile_90d", 50)

        if price_percentile > 85:
            enhanced_score += 4
        elif price_percentile < 20:
            enhanced_score -= 3

        # ---------------------------------------
        # Risk Adjustment
        # ---------------------------------------
        volatility = latest.get("volatility", 1)
        risk_adjusted_score = enhanced_score / (1 + volatility)

        enhanced_score = max(0, min(100, enhanced_score))

        rankings.append({
            "symbol": symbol,
            "score": base_score,
            "enhanced_score": enhanced_score,
            "risk_adjusted_score": risk_adjusted_score
        })

    ranking_df = pd.DataFrame(rankings)

    ranking_df.sort_values(
        by="risk_adjusted_score",
        ascending=False,
        inplace=True
    )

    ranking_df["rank"] = range(1, len(ranking_df) + 1)

    return ranking_df