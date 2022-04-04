import func_arbitrage
import json
import time

# Set variables
coin_price_url = "https://poloniex.com/public?command=returnTicker"


def step_0():
    """
    Step 0: Finding coins which can be traded.
    See: https://docs.poloniex.com/#http-api  for the url endpoints etc.
    """

    # Extract list of coins and prices from exchange
    coin_json = func_arbitrage.get_coin_tickers(coin_price_url)

    coin_list = func_arbitrage.collect_tradeables(coin_json)

    print(f'tradeable pairs: {len(coin_list)}')

    # return list of tradeable coins
    return coin_list


def step_1(coin_list):
    """
    Step 1: Structuring Triangular Pairs
    Can take a couple of minutes,
    but this only needs to be executed once, then update daily or weekly.
    """
    # structure the list of tradeable arbitrage pairs
    structured_list = func_arbitrage.structure_triangular_pairs(coin_list)

    # Save structured list
    with open("structured_triangular_pairs.json", "w") as json_file:
        json.dump(structured_list, json_file)


def step_2():
    """
    Step 2: Calculate Surface Arbitrage Opportunities
    Using Poloniex.
    """

    # Get Structured Pairs
    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)

    # Get Latest Surface Prices
    prices_json = func_arbitrage.get_coin_tickers(
        coin_price_url)  # same data as step 0

    # Loot through and structure price information
    while True:
        time.sleep(0.5)
        for t_pair in structured_pairs:
            prices_dict = func_arbitrage.get_price_for_t_pair(
                t_pair, prices_json)
            surface_arb = func_arbitrage.calc_triangular_arb_surface_rate(
                t_pair, prices_dict)
            if len(surface_arb) > 0:
                print(surface_arb)


""" MAIN """

if __name__ == "__main__":
    # coin_list = step_0()
    # structured_pairs = step_1(coin_list)
    step_2()
