def build_detailed_report(
    market_regime,
    rolling_accuracy,
    expectancy,
    breadth,
    portfolio_metrics,
    ranking_df,
    signals_dict
):

    header = f"""
📊 AUTONOMOUS FINANCIAL INTELLIGENCE REPORT

Market Regime: {market_regime}
Rolling Accuracy: {rolling_accuracy}%
Strategy Expectancy: {expectancy}
Market Breadth: {round(breadth, 2)}

📈 Portfolio Metrics
Total Return: {portfolio_metrics.get('total_return_%', 0)}%
Max Drawdown: {portfolio_metrics.get('max_drawdown_%', 0)}%
Sharpe Ratio: {portfolio_metrics.get('sharpe_ratio', 0)}
Final Capital: ₹{portfolio_metrics.get('final_value', 0)}

------------------------------------------------
📌 TOP RANKED STOCKS
"""

    ranking_section = ""

    for _, row in ranking_df.head(5).iterrows():
        symbol = row["symbol"]
        ranking_section += f"\n{symbol} → Rank #{row['rank']} | Score: {round(row['enhanced_score'],2)}"

    signals_section = "\n\n------------------------------------------------\n📢 DAILY SIGNALS\n"

    for symbol, data in signals_dict.items():
        signals_section += (
            f"\n{symbol} → {data['signal']} "
            f"(Conf: {data['confidence']}%)"
        )

    footer = "\n\n⚙️ System Status: ACTIVE"

    return header + ranking_section + signals_section + footer