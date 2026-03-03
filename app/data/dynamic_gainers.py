import yfinance as yf
import pandas as pd

from config import NIFTY_50_LIST
from app.utils.logger import get_logger

logger = get_logger()


def fetch_top_gainers(limit=5):
    """
    Fetch top N gainers from NIFTY 50 list based on
    1-day percentage change using last 5 trading days.

    This is ONLY for universe selection.
    It does NOT affect historical backtesting depth.
    """

    try:
        df = yf.download(
            tickers=NIFTY_50_LIST,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True
        )

        if df is None or df.empty:
            logger.warning("Dynamic gainers: empty dataframe returned.")
            return []

        gainers = []

        # Ensure MultiIndex structure
        if not isinstance(df.columns, pd.MultiIndex):
            logger.warning("Dynamic gainers: unexpected dataframe structure.")
            return []

        available_symbols = df.columns.get_level_values(0).unique()

        for symbol in NIFTY_50_LIST:

            try:
                if symbol not in available_symbols:
                    continue

                stock_df = df[symbol].dropna()

                if "Close" not in stock_df.columns:
                    continue

                if len(stock_df) < 2:
                    continue

                yesterday_close = float(stock_df["Close"].iloc[-2])
                today_close = float(stock_df["Close"].iloc[-1])

                if yesterday_close == 0:
                    continue

                pct_change = (
                    (today_close - yesterday_close) /
                    yesterday_close
                ) * 100

                gainers.append({
                    "symbol": symbol,
                    "pct_change": pct_change
                })

            except Exception as inner_error:
                logger.debug(
                    f"Dynamic gainers: error processing {symbol}: {inner_error}"
                )
                continue

        if not gainers:
            logger.info("Dynamic gainers: no valid gainers found.")
            return []

        df_all = pd.DataFrame(gainers)
        df_all.sort_values(
            by="pct_change",
            ascending=False,
            inplace=True
        )

        top_symbols = df_all.head(limit)["symbol"].tolist()

        logger.info(
            f"Dynamic gainers selected: {top_symbols}"
        )

        return top_symbols

    except Exception as e:
        logger.error(f"Dynamic gainers failure: {e}", exc_info=True)
        return []