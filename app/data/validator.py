import pandas as pd
from app.utils.logger import get_logger

logger = get_logger()


def validate_stock_data(df: pd.DataFrame) -> bool:
    """
    Validates required OHLCV columns.
    Date must be in index (DatetimeIndex).
    """

    if df is None or df.empty:
        logger.warning("Stock validation failed: Empty dataframe.")
        return False

    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        logger.warning("Stock validation failed: Index is not DatetimeIndex.")
        return False

    required_columns = ["Open", "High", "Low", "Close", "Volume"]

    for col in required_columns:
        if col not in df.columns:
            logger.warning(f"Stock validation failed: Missing column {col}.")
            return False

    return True