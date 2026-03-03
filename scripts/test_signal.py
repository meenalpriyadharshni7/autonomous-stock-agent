from config import CORE_STOCKS
from app.data.fetcher import fetch_stock_data
from app.data.validator import validate_stock_data
from app.analytics.indicators import apply_all_indicators
from app.decision.signal_engine import classify_signal


def test_signals():
    for symbol in CORE_STOCKS[:5]:
        df = fetch_stock_data(symbol)

        if not validate_stock_data(df):
            continue

        df = apply_all_indicators(df)
        latest = df.iloc[-1]

        signal, confidence, reasons = classify_signal(latest)

        print(f"\n{symbol}")
        print("Signal:", signal)
        print("Confidence:", confidence)
        print("Reasons:", reasons)


if __name__ == "__main__":
    test_signals()