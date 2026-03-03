import yfinance as yf
import pandas as pd
import time
from datetime import timedelta
from config import HISTORICAL_DAYS

from app.utils.time_utils import get_ist_datetime
from app.utils.logger import get_logger
from app.data.cache_manager import load_from_cache, save_to_cache

logger = get_logger()


def fetch_stock_data(symbol: str, retries: int = 3, debug: bool = False) -> pd.DataFrame:
    """
    Production-grade fetcher with:

    ✔ Local caching
    ✔ Incremental updates
    ✔ Yahoo fallback
    ✔ Numeric sanitization
    ✔ Volume filtering
    ✔ Duplicate removal
    ✔ Safe failure handling
    """

    end_date = get_ist_datetime() + timedelta(days=1)

    # =====================================================
    # 1️⃣ LOAD CACHE
    # =====================================================
    cached_df = load_from_cache(symbol)

    if not cached_df.empty:
        last_cached_date = cached_df.index.max()
        start_date = last_cached_date + timedelta(days=1)
    else:
        start_date = end_date - timedelta(days=HISTORICAL_DAYS)

    new_data = pd.DataFrame()

    # =====================================================
    # 2️⃣ FETCH MISSING DATA
    # =====================================================
    for attempt in range(retries):
        try:
            df = yf.download(
                tickers=symbol,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False
            )

            # Fallback to period-based if incremental fails
            if df is None or df.empty:
                logger.warning(f"{symbol}: incremental fetch empty. Trying fallback.")
                df = yf.download(
                    tickers=symbol,
                    period="1y",
                    interval="1d",
                    auto_adjust=False,
                    progress=False,
                    threads=False
                )

            if df is None or df.empty:
                raise ValueError("Empty dataframe after fallback")

            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)

            new_data = df
            break

        except Exception as e:
            logger.warning(
                f"{symbol}: Retry {attempt + 1}/{retries} failed: {e}"
            )
            time.sleep(1)

    # =====================================================
    # 3️⃣ MERGE CACHE + NEW DATA
    # =====================================================
    if not cached_df.empty and not new_data.empty:
        combined = pd.concat([cached_df, new_data])
    elif not cached_df.empty:
        combined = cached_df
    elif not new_data.empty:
        combined = new_data
    else:
        logger.error(f"{symbol}: No data available after retries.")
        return pd.DataFrame()

    # Remove duplicates after merge
    combined = combined[~combined.index.duplicated(keep="last")]

    # =====================================================
    # 4️⃣ CLEAN & VALIDATE
    # =====================================================
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    combined = combined[[col for col in required_cols if col in combined.columns]]

    for col in combined.columns:
        combined[col] = pd.to_numeric(combined[col], errors="coerce")

    combined.dropna(inplace=True)

    if "Volume" in combined.columns:
        combined = combined[combined["Volume"] > 0]

    combined = combined.sort_index()

    if len(combined) < 50:
        logger.warning(f"{symbol}: Insufficient data depth ({len(combined)} rows).")
        return pd.DataFrame()

    combined["symbol"] = symbol

    # =====================================================
    # 5️⃣ SAVE UPDATED CACHE
    # =====================================================
    try:
        save_to_cache(symbol, combined)
    except Exception as e:
        logger.error(f"{symbol}: Cache save failed: {e}")

    # =====================================================
    # 6️⃣ DEBUG OUTPUT
    # =====================================================
    if debug:
        logger.info("========================================")
        logger.info(f"DATA SOURCE FOR: {symbol}")
        logger.info(f"Start: {combined.index.min()}")
        logger.info(f"End: {combined.index.max()}")
        logger.info(f"Total Rows: {len(combined)}")
        logger.info(f"Last 5 Rows:\n{combined.tail()}")
        logger.info("========================================")

    return combined