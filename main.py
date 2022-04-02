import func_arbitrage
import json


def step_0():
    """
    Step 0: Finding coins which can be traded.
    See: https://docs.poloniex.com/#http-api  for the url endpoints etc.
    """

    # Extract list of coins and prices from exchange
    url = "https://poloniex.com/public?command=returnTicker"
    coin_json = func_arbitrage.get_coin_tickers(url)

    coin_list = func_arbitrage.collect_tradeables(coin_json)

    print(f'tradeable pairs: {len(coin_list)}')

    # return list of tradeable coins
    return coin_list


def step_1(coin_list):
    """
    Step 1: Structuring Triangular Pairs
    """
    # structure the list of tradeable arbitrage pairs
    structured_list = func_arbitrage.structure_triangular_pairs(coin_list)

    # Save structured list
    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(structured_list, fp)


""" MAIN """

if __name__ == "__main__":
    coin_list = step_0()
    structured_pairs = step_1(coin_list)
