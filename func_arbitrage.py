from os import remove
import requests
import json


def get_coin_tickers(url):
    # Make a get request

    req = requests.get(url)
    json_resp = json.loads(req.text)
    return json_resp


def collect_tradeables(json_obj):
    # Loop through each object and find the tradeable pairs
    pair_list = []
    for pair in json_obj:
        is_frozen = json_obj[pair]["isFrozen"]
        is_post_only = json_obj[pair]["postOnly"]
        if is_frozen == "0" and is_post_only == "0":
            pair_list.append(pair)
    return pair_list


def structure_triangular_pairs(coin_list):
    # Structure Arbitrage Pairs

    # Declare variables
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:]

    # Get Pair A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("_")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # Assign A to a Box
        a_pair_box = [a_base, a_quote]

        # Get Pair B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("_")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # Check Pair B
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # Get Pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("_")
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]

                        # Count the number of matching C items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base,
                                        b_quote, c_base, c_quote]

                            counts_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    counts_c_base += 1

                            counts_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    counts_c_quote += 1

                            # Determining Triangular Match
                            if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                                combined = f'{pair_a}, {pair_b}, {pair_c}'

                                # sort combined pairs alphabetically and ensure that duplicates get removed:
                                unique_item = ''.join(sorted(combine_all))
                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)
    print(f'triangular pairs found: {len(triangular_pairs_list)}')
    # print(triangular_pairs_list[0:20])
    return triangular_pairs_list


def get_price_for_t_pair(t_pair, prices_json):
    # Structure Prices

    # Extract pair info
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract price information for given pairs
    pair_a_ask = float(prices_json[pair_a]["lowestAsk"])
    pair_a_bid = float(prices_json[pair_a]["highestBid"])
    # print(pair_a_ask, pair_a_bid)
    pair_b_ask = float(prices_json[pair_b]["lowestAsk"])
    pair_b_bid = float(prices_json[pair_b]["highestBid"])
    pair_c_ask = float(prices_json[pair_c]["lowestAsk"])
    pair_c_bid = float(prices_json[pair_c]["highestBid"])

    # output dictionary
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid
    }


def calc_triangular_arb_surface_rate(t_pair, prices_dict):
    # Calculate Surface Rate Arbitrage Opportunity

    # Set variables
    starting_amount = 1  # how many initial coins do we start out with?
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t1 = 0
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0   # changes to 1 once we traded a full group.

    # Extract Pair Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Price Information
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]

    # Set directions and loop through
    # "direction" meaning: forward = Base -> Quote, reverse = Quote -> Base
    direction_list = ["forward", "reverse"]
    for direction in direction_list:
        # set additional variables for swap information
        swap_1 = 0
        swap_2 = 0  # coins
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0  # prices
        swap_3_rate = 0

        # Assume starting with a_base and swapping for a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            # Poloniex rule: going from base to quote -> *(1/Ask)
            swap_1_rate = 1 / a_ask
            direction_trade_1 = "base_to_quote"

        # Assume starting with a_quote and swapping for a_base
        if direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = "quote_to_base"

        # Place first trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount * swap_1_rate
        # print(
        #     f'{direction} Trade1: {pair_a} starting amount: {starting_amount}, acquired amount: {acquired_coin_t1}')

        """ FORWARD """
        # Scenario Forward-B: second pair contains the token of our first trade.

        # Check if a_quote (acquired coin) matches b_quote
        if direction == "forward":
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_bid  # because in 2nd trade we go from right to left
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If above matches, we've now acquired b_base.
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 * c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Check if a_quote (acquired coin) matches b_base
        if direction == "forward":
            if a_quote == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If above matches, we've now acquired b_quote.
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 * c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Scenario Forward-C: third pair contains the token of our first trade.

        # Check if a_quote (acquired coin) matches c_quote
        if direction == "forward":
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_bid  # because in 2nd trade we go from right to left
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If above matches, we've now acquired c_base.
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 * b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Check if a_quote (acquired coin) matches c_base
        if direction == "forward":
            if a_quote == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If above matches, we've now acquired c_quote.
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 * b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # print out potential opportunities
            # if acquired_coin_t3 > starting_amount:
            #     print(direction, pair_a, pair_b, pair_c,
            #           starting_amount, acquired_coin_t3)

        """ REVERSE """
        # Scenario Reverse-B: second pair contains the token of our first trade.

        # Check if a_base (acquired coin) matches b_quote
        if direction == "reverse":
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_bid  # because in 2nd trade we go from right to left
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If above matches, we've now acquired b_base.
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Check if a_base (acquired coin) matches b_base
        if direction == "reverse":
            if a_base == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If above matches, we've now acquired b_quote.
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = 1 * c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Scenario Reverse-C: third pair contains the token of our first trade.

        # Check if a_base (acquired coin) matches c_quote
        if direction == "reverse":
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_bid  # because in 2nd trade we go from right to left
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If above matches, we've now acquired c_base.
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = 1 * b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Check if a_base (acquired coin) matches c_base
        if direction == "reverse":
            if a_base == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If above matches, we've now acquired c_quote.
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

            # print out potential opportunities
            # if acquired_coin_t3 > starting_amount:
            #     print(direction, pair_a, pair_b, pair_c,
            #           starting_amount, acquired_coin_t3)

        """ PROFIT LOSS OUTPUT """

        # Profit and Loss Calculations
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * \
            100 if profit_loss != 0 else 0

        # Trade Descriptions for debugging
        trade_description_1 = f"start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}"
        trade_description_2 = f"start with {acquired_coin_t1} of {swap_2}. Swap at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}"
        trade_description_3 = f"start with {acquired_coin_t2} of {swap_3}. Swap at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}"

        # if profit_loss > 0:
        #     print("NEW TRADE")
        #     print(direction, pair_a, pair_b, pair_c)
        #     print(trade_description_1)
        #     print(trade_description_2)
        #     print(trade_description_3)

        # Output Results
        if profit_loss_perc > min_surface_rate:
            surface_dict = {
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "starting_amount": starting_amount,
                "acquired_coin_t1": acquired_coin_t1,
                "acquired_coin_t2": acquired_coin_t2,
                "acquired_coin_t3": acquired_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "profit_loss": profit_loss,
                "profit_loss_perc": profit_loss_perc,
                "direction": direction,
                "trade_description_1": trade_description_1,
                "trade_description_2": trade_description_2,
                "trade_description_3": trade_description_3
            }
            return surface_dict  # if profitable will return forward calc, and not do reverse calc
    return surface_dict
