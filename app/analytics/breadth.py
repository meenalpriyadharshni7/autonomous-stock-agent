def compute_market_breadth(stock_data_dict):
    """
    Computes simple market breadth:
    % of stocks trading above their 20-day MA.
    """

    if not stock_data_dict:
        return 0

    total = len(stock_data_dict)
    bullish = 0

    for symbol, df in stock_data_dict.items():
        latest = df.iloc[-1]

        if latest.get("Close", 0) > latest.get("ma20", 0):
            bullish += 1

    breadth = (bullish / total) * 100
    return round(breadth, 2)