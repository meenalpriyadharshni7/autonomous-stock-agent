import os
import pandas as pd
from datetime import datetime

CACHE_DIR = "data_cache"


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_cache_path(symbol: str) -> str:
    ensure_cache_dir()
    safe_symbol = symbol.replace("^", "")
    return os.path.join(CACHE_DIR, f"{safe_symbol}.csv")


def load_from_cache(symbol: str) -> pd.DataFrame:
    path = get_cache_path(symbol)

    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df.sort_index(inplace=True)
    return df


def save_to_cache(symbol: str, df: pd.DataFrame):
    path = get_cache_path(symbol)

    df_to_save = df.copy()
    df_to_save.reset_index(inplace=True)
    df_to_save.to_csv(path, index=False)