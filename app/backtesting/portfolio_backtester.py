import pandas as pd
import numpy as np

from app.analytics.indicators import apply_all_indicators
from app.analytics.scoring import compute_score
from app.analytics.breadth import compute_market_breadth
from app.utils.logger import get_logger

logger = get_logger()


class PortfolioBacktester:

    def __init__(
        self,
        initial_capital=100000,
        lookback_days=250,
        holding_period=5,
        top_n=5,
        brokerage_rate=0.001,
        slippage_rate=0.0005,
        stop_loss_pct=0.03,
        daily_drawdown_limit=0.02,
        max_position_weight=0.30,
        debug=False
    ):
        self.initial_capital = initial_capital
        self.lookback_days = lookback_days
        self.holding_period = holding_period
        self.top_n = top_n
        self.brokerage_rate = brokerage_rate
        self.slippage_rate = slippage_rate
        self.stop_loss_pct = stop_loss_pct
        self.daily_drawdown_limit = daily_drawdown_limit
        self.max_position_weight = max_position_weight
        self.debug = debug

    # =====================================================
    # MAIN BACKTEST ENGINE
    # =====================================================
    def run(self, stock_data_dict, market_regime):

        if not stock_data_dict:
            return [], []

        portfolio_value = self.initial_capital
        equity_curve = []
        daily_returns = []
        exposure_modifier = 1.0

        # Ensure datetime index
        for symbol, df in stock_data_dict.items():
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
                stock_data_dict[symbol] = df.sort_index()

        reference_symbol = max(
            stock_data_dict,
            key=lambda s: len(stock_data_dict[s])
        )

        reference_df = stock_data_dict[reference_symbol]
        required_bars = self.lookback_days + self.holding_period + 10

        if len(reference_df) < required_bars:
            return [], []

        start_index = len(reference_df) - self.lookback_days - self.holding_period

        for i in range(start_index, len(reference_df) - self.holding_period):

            buy_candidates = {}
            sliced_data = {}

            # ---------------------------------------------
            # Build historical slice per symbol
            # ---------------------------------------------
            for symbol, df in stock_data_dict.items():

                if len(df) <= i:
                    continue

                historical_slice = df.iloc[:i+1].copy()

                if len(historical_slice) < 50:
                    continue

                historical_slice = apply_all_indicators(historical_slice)
                historical_slice["score"] = historical_slice.apply(
                    compute_score,
                    axis=1
                )

                latest = historical_slice.iloc[-1]
                enhanced_score = latest.get("score", 0)

                sliced_data[symbol] = historical_slice
                buy_candidates[symbol] = {
                    "enhanced_score": enhanced_score
                }

            if not sliced_data:
                equity_curve.append(portfolio_value)
                daily_returns.append(0)
                continue

            breadth = compute_market_breadth(sliced_data)

            ranked = sorted(
                buy_candidates.items(),
                key=lambda x: x[1]["enhanced_score"],
                reverse=True
            )

            top_n = ranked[:self.top_n]

            if not top_n:
                equity_curve.append(portfolio_value)
                daily_returns.append(0)
                continue

            # ---------------------------------------------
            # Market Exposure Scaling
            # ---------------------------------------------
            trend = market_regime.get("trend", "neutral")
            vol = market_regime.get("volatility", "normal")

            trend_multiplier = {
                "bullish": 1.0,
                "neutral": 0.7,
                "bearish": 0.4
            }.get(trend, 0.7)

            vol_multiplier = {
                "low": 1.1,
                "normal": 1.0,
                "high": 0.8
            }.get(vol, 1.0)

            base_exposure = trend_multiplier * vol_multiplier
            exposure = base_exposure * exposure_modifier

            total_score = sum(
                max(1, data["enhanced_score"])
                for _, data in top_n
            )

            total_profit = 0
            previous_value = portfolio_value

            # =====================================================
            # ALLOCATION LOOP
            # =====================================================
            for symbol, data in top_n:

                df = stock_data_dict[symbol]

                entry_date = reference_df.index[i]
                exit_date = reference_df.index[i + self.holding_period]

                try:
                    entry_price = df.loc[:entry_date].iloc[-1]["Close"]
                except Exception:
                    continue

                exit_price = None

                # Stop-loss check
                for forward in range(1, self.holding_period + 1):

                    check_date = reference_df.index[i + forward]

                    try:
                        price = df.loc[:check_date].iloc[-1]["Close"]
                    except Exception:
                        continue

                    if price <= entry_price * (1 - self.stop_loss_pct):
                        exit_price = price
                        break

                if exit_price is None:
                    try:
                        exit_price = df.loc[:exit_date].iloc[-1]["Close"]
                    except Exception:
                        continue

                score = max(1, data["enhanced_score"])
                weight = (score / total_score) * exposure
                weight = min(weight, self.max_position_weight)

                capital_allocated = portfolio_value * weight

                # Apply slippage
                entry_price *= (1 + self.slippage_rate)
                exit_price *= (1 - self.slippage_rate)

                shares = capital_allocated / entry_price
                gross_exit_value = shares * exit_price

                # Apply brokerage
                entry_cost = capital_allocated * self.brokerage_rate
                exit_cost = gross_exit_value * self.brokerage_rate

                net_exit_value = gross_exit_value - exit_cost
                total_invested = capital_allocated + entry_cost

                profit = net_exit_value - total_invested
                total_profit += profit

                if self.debug:
                    logger.debug(
                        f"[BACKTEST] {symbol} | "
                        f"Entry={entry_price:.2f} | "
                        f"Exit={exit_price:.2f} | "
                        f"Weight={weight:.3f} | "
                        f"Profit={profit:.2f}"
                    )

            portfolio_value += total_profit

            daily_return = (
                total_profit / previous_value
                if previous_value != 0 else 0
            )

            # Daily drawdown guard
            if daily_return < -self.daily_drawdown_limit:
                exposure_modifier *= 0.5
            else:
                exposure_modifier = min(1.0, exposure_modifier + 0.05)

            equity_curve.append(portfolio_value)
            daily_returns.append(daily_return)

        return equity_curve, daily_returns


# =====================================================
# PORTFOLIO METRICS
# =====================================================
def compute_portfolio_metrics(equity_curve, daily_returns, initial_capital=100000):

    if not equity_curve:
        return {
            "total_return_%": 0.0,
            "max_drawdown_%": 0.0,
            "sharpe_ratio": 0.0,
            "final_value": float(initial_capital)
        }

    equity_series = pd.Series(equity_curve)

    total_return = (
        (equity_series.iloc[-1] / equity_series.iloc[0]) - 1
    ) * 100

    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    returns_series = pd.Series(daily_returns)

    sharpe = 0
    if returns_series.std() != 0:
        sharpe = (
            returns_series.mean() /
            returns_series.std()
        ) * np.sqrt(252)

    return {
        "total_return_%": float(round(total_return, 2)),
        "max_drawdown_%": float(round(max_drawdown, 2)),
        "sharpe_ratio": float(round(sharpe, 2)),
        "final_value": float(round(equity_series.iloc[-1], 2))
    }