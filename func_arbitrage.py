import requests
import json

# Make a get request


def get_coin_tickers(url):
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
