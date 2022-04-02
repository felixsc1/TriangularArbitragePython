# Triangular Arbitrage

Python script based on tutorial on cryptowizards.net

The code in main.py is divided into the individual steps:

## Step 1: Find all triangular pairs

In pseudocode:
1. Start with a pair A, e.g. USDT_BTC
2. Loop through list of all tradeable pairs. Find pair that contains one token of pair A, e.g. BTC_ETH. -> this becomes pair B.
3. Find another pair C that contains one token of pair A, one of pair B, such that each token appears twice. (In the example, USDT_ETH)
4. Add these three pairs to a list, repeat the steps 1-3 with a new starting pair.

Result is stored in json format for subsequent use.

## Step 2:  ...
to be continued...