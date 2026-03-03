from config import CORE_STOCKS
from app.data.dynamic_gainers import fetch_top_gainers


def test_universe():
    gainers = fetch_top_gainers(limit=5)

    final_universe = list(set(CORE_STOCKS + gainers))

    print("Top 5 Gainers:", gainers)
    print("Final Universe Count:", len(final_universe))
    print("Final Universe:", final_universe)


if __name__ == "__main__":
    test_universe()