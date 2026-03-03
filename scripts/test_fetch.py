from app.data.fetcher import fetch_stock_data
from app.data.validator import validate_stock_data
from config import CORE_STOCKS


def test_fetch():
    for stock in CORE_STOCKS[:2]:
        df = fetch_stock_data(stock)
        if validate_stock_data(df):
            print(f"✅ {stock} data valid. Rows: {len(df)}")
        else:
            print(f"❌ {stock} invalid data.")


if __name__ == "__main__":
    test_fetch()