from sqlalchemy import select

from config import CORE_STOCKS, HISTORICAL_DAYS

from app.data.dynamic_gainers import fetch_top_gainers
from app.data.fetcher import fetch_stock_data
from app.data.validator import validate_stock_data

from app.analytics.indicators import apply_all_indicators
from app.analytics.scoring import compute_score
from app.analytics.baseline import HistoricalBaselineEngine
from app.analytics.ranking import rank_stocks
from app.analytics.market_regime import MarketRegimeEngine
from app.analytics.breadth import compute_market_breadth

from app.decision.signal_engine import classify_signal
from app.decision.confidence import adjust_confidence

from app.memory.db import SessionLocal
from app.memory.models import DailyMetrics, Signal, ExecutionLog

from app.backtesting.accuracy_tracker import AccuracyTracker
from app.backtesting.performance_metrics import PerformanceMetrics
from app.backtesting.portfolio_backtester import (
    PortfolioBacktester,
    compute_portfolio_metrics
)

from app.notification.telegram_bot import send_telegram_message
from app.notification.email_sender import send_email

from app.backtesting.accuracy_backfill import backfill_accuracy
from app.utils.logger import get_logger
from app.utils.time_utils import get_ist_date
from app.utils.market_calendar import is_nse_trading_day


logger = get_logger()


# =====================================================
# REPORT BUILDER
# =====================================================
def build_daily_report(
    market_regime,
    rolling_accuracy,
    expectancy,
    breadth,
    portfolio_metrics,
    ranking_df,
    signals_dict,
    is_trading_day
):

    status_note = (
        "🟢 LIVE TRADING DAY"
        if is_trading_day
        else "🔵 MARKET CLOSED – Showing Last Available Data"
    )

    header = f"""
{status_note}

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
📌 TOP 5 RANKED STOCKS
"""

    ranking_section = ""
    for _, row in ranking_df.head(5).iterrows():
        ranking_section += (
            f"\n{row['symbol']} → Rank #{row['rank']} "
            f"| Score: {round(row['enhanced_score'], 2)}"
        )

    signals_section = "\n\n------------------------------------------------\n📢 DAILY SIGNALS\n"

    for symbol, data in signals_dict.items():
        signals_section += (
            f"\n{symbol} → {data['signal']} "
            f"(Conf: {data['confidence']}%)"
        )

    footer = "\n\n⚙️ System Status: ACTIVE"

    return header + ranking_section + signals_section + footer


# =====================================================
# UNIVERSE BUILDER
# =====================================================
def build_universe():
    top_gainers = fetch_top_gainers(limit=10)
    final_universe = CORE_STOCKS.copy()

    for symbol in top_gainers:
        if symbol not in final_universe:
            final_universe.append(symbol)
        if len(final_universe) == 15:
            break

    return final_universe


# =====================================================
# MAIN PIPELINE
# =====================================================
def run_pipeline(debug_fetch=False):

    logger.info("Starting Autonomous Financial Decision Intelligence System")
    logger.info(f"Configured Historical Days: {HISTORICAL_DAYS}")

    db = SessionLocal()

    try:
        today = get_ist_date()
        is_trading_day = is_nse_trading_day()

        # -----------------------------------------
        # Idempotent Execution (Trading Days Only)
        # -----------------------------------------
        if is_trading_day:
            existing_entry = db.execute(
                select(DailyMetrics).where(DailyMetrics.date == today)
            ).first()

            if existing_entry:
                logger.warning("Data already exists for today. Skipping execution.")
                return

        # -----------------------------------------
        # Universe
        # -----------------------------------------
        final_universe = build_universe()
        logger.info(f"Universe Count: {len(final_universe)}")

        # -----------------------------------------
        # Market Regime
        # -----------------------------------------
        market_engine = MarketRegimeEngine()
        market_regime = market_engine.detect_regime()
        market_regime["momentum"] = float(market_regime.get("momentum", 0))
        logger.info(f"Market Regime: {market_regime}")

        stock_data = {}
        baseline_engine = HistoricalBaselineEngine(window=90)

        # -----------------------------------------
        # Fetch + Indicators
        # -----------------------------------------
        for symbol in final_universe:

            df = fetch_stock_data(symbol, debug=debug_fetch)

            if not validate_stock_data(df):
                logger.warning(f"Skipping invalid data for {symbol}")
                continue

            df = apply_all_indicators(df)
            df["score"] = df.apply(compute_score, axis=1)

            relative_metrics = baseline_engine.compute_relative_metrics(df)

            for key, value in relative_metrics.items():
                df.loc[df.index[-1], key] = value

            stock_data[symbol] = df

        if not stock_data:
            raise ValueError("No valid stock data available.")

        # -----------------------------------------
        # Backfill Accuracy
        # -----------------------------------------
        backfill_accuracy(
            db=db,
            stock_data_dict=stock_data,
            market_regime=market_regime,
            holding_period=5
        )

        # -----------------------------------------
        # Market Breadth
        # -----------------------------------------
        breadth = compute_market_breadth(stock_data)

        # -----------------------------------------
        # Ranking
        # -----------------------------------------
        ranking_df = rank_stocks(stock_data)

        # -----------------------------------------
        # Accuracy + Expectancy
        # -----------------------------------------
        accuracy_tracker = AccuracyTracker(db)

        if is_trading_day:
            accuracy_tracker.evaluate_signals(today)

        rolling_accuracy = accuracy_tracker.compute_rolling_accuracy()

        performance_engine = PerformanceMetrics(db)
        metrics = performance_engine.compute_metrics()
        expectancy = metrics["expectancy"]

        # -----------------------------------------
        # Generate Signals
        # -----------------------------------------
        signals_dict = {}

        for _, row in ranking_df.iterrows():

            symbol = row["symbol"]
            enhanced_score = float(row["enhanced_score"])
            latest = stock_data[symbol].iloc[-1]

            signal, base_confidence, reasons = classify_signal(
                latest,
                enhanced_score,
                market_regime,
                breadth
            )

            final_confidence = adjust_confidence(
                base_confidence,
                rolling_accuracy,
                market_regime,
                expectancy,
                breadth
            )

            signals_dict[symbol] = {
                "signal": signal,
                "confidence": final_confidence
            }

            if is_trading_day:
                db.add(DailyMetrics(
                    stock_symbol=symbol,
                    date=today,
                    category="CORE" if symbol in CORE_STOCKS else "GAINER",
                    close_price=float(latest["Close"]),
                    rsi=float(latest["rsi"]),
                    ma20=float(latest["ma20"]),
                    ma50=float(latest["ma50"]),
                    volatility=float(latest["volatility"]),
                    momentum_7d=float(latest["momentum_7d"]),
                    momentum_30d=float(latest["momentum_30d"]),
                    score=float(row["score"]),
                    rank=int(row["rank"])
                ))

                db.add(Signal(
                    stock_symbol=symbol,
                    date=today,
                    signal=signal,
                    confidence=float(final_confidence),
                    reason_tags=", ".join(reasons)
                ))

        # -----------------------------------------
        # Portfolio Backtest
        # -----------------------------------------
        portfolio_backtester = PortfolioBacktester(
            initial_capital=100000,
            lookback_days=250,
            holding_period=5,
            debug=False
        )

        equity_curve, daily_returns = portfolio_backtester.run(
            stock_data,
            market_regime
        )

        portfolio_metrics = compute_portfolio_metrics(
            equity_curve,
            daily_returns,
            initial_capital=100000
        )

        # -----------------------------------------
        # Build Report
        # -----------------------------------------
        report_message = build_daily_report(
            market_regime,
            rolling_accuracy,
            expectancy,
            breadth,
            portfolio_metrics,
            ranking_df,
            signals_dict,
            is_trading_day
        )

        # -----------------------------------------
        # Telegram (Guaranteed Safe)
        # -----------------------------------------
        try:
            logger.info("Sending Telegram message...")
            send_telegram_message(report_message)
            logger.info("Telegram send attempted.")
        except Exception as e:
            logger.error(f"Telegram failed: {e}", exc_info=True)

        # -----------------------------------------
        # Email (Non-blocking)
        # -----------------------------------------
        try:
            logger.info("Sending Email...")
            send_email(
                subject="Autonomous Financial Intelligence Report",
                message=report_message
            )
        except Exception as e:
            logger.error(f"Email failed: {e}", exc_info=True)

        if is_trading_day:
            db.commit()

        db.add(ExecutionLog(
            status="SUCCESS",
            message="Pipeline executed successfully"
        ))
        db.commit()

        logger.info("Execution completed successfully.")

    except Exception as e:

        db.rollback()
        logger.error(f"Pipeline failed: {e}", exc_info=True)

        try:
            send_telegram_message(f"⚠️ Agent execution FAILED:\n{e}")
        except Exception:
            pass

        try:
            db.add(ExecutionLog(
                status="FAILURE",
                message=str(e)
            ))
            db.commit()
        except Exception:
            pass

    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline(debug_fetch=False)