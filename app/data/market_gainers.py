import yfinance as yf
import pandas as pd
import time


class MarketGainersEngine:
    """
    Responsible for fetching and validating top market gainers.
    """

    def __init__(self, retries=3, delay=2):
        self.retries = retries
        self.delay = delay

    def _safe_download(self, symbol):
        for attempt in range(self.retries):
            try:
                df = yf.download(symbol, period="5d", progress=False)
                if not df.empty:
                    return df
            except Exception:
                time.sleep(self.delay)
        return None

    def filter_valid_symbols(self, symbols):
        """
        Removes delisted or invalid stocks.
        """
        valid = []

        for symbol in symbols:
            df = self._safe_download(symbol)
            if df is not None:
                valid.append(symbol)

        return valid

    def get_top_gainers(self, raw_symbols):
        """
        Final cleaned list.
        """
        raw_symbols = list(set(raw_symbols))
        return self.filter_valid_symbols(raw_symbols)