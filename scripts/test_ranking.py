from config import CORE_STOCKS
from app.data.fetcher import fetch_stock_data
from app.data.validator import validate_stock_data
from app.analytics.indicators import apply_all_indicators
from app.analytics.ranking import rank_stocks


def test_ranking():
    stock_data = {}

    for symbol in CORE_STOCKS[:5]:
        df = fetch_stock_data(symbol)

        if not validate_stock_data(df):
            continue

        df = apply_all_indicators(df)
        stock_data[symbol] = df

    ranking = rank_stocks(stock_data)

    print("\n📊 Stock Rankings:\n")
    print(ranking)


if __name__ == "__main__":
    test_ranking()