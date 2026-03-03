from app.data.fetcher import fetch_stock_data
from app.data.validator import validate_stock_data
from app.analytics.indicators import apply_all_indicators


def test_indicators():
    df = fetch_stock_data("TCS.NS")

    if not validate_stock_data(df):
        print("Invalid data")
        return

    df = apply_all_indicators(df)

    latest = df.iloc[-1]

    print("Latest Metrics:")
    print("Close:", latest["Close"])
    print("MA20:", latest["ma20"])
    print("MA50:", latest["ma50"])
    print("RSI:", latest["rsi"])
    print("Momentum 7D:", latest["momentum_7d"])
    print("Volatility:", latest["volatility"])
    print("Volume Ratio:", latest["volume_ratio"])


if __name__ == "__main__":
    test_indicators()