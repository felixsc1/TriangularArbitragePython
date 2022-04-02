import func_arbitrage

"""
    Step 0: Finding coins which can be traded.
    See: https://docs.poloniex.com/#http-api  for the url endpoints etc.
"""


def step_0():

    # Extract list of coins and prices from exchange
    url = "https://poloniex.com/public?command=returnTicker"
    coin_json = func_arbitrage.get_coin_tickers(url)

    coin_list = func_arbitrage.collect_tradeables(coin_json)

    print(f'tradeable pairs: {len(coin_list)}')

    return coin_list


""" MAIN """

if __name__ == "__main__":
    coin_list = step_0()
