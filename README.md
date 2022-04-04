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

## Step 2: Calculating the surface rate

Note: The poloniex exchange is used here, format of data may differ on other exchanges.

Pairs are given in the format "USDT_BTC",
the left is the Base, the right is the Quote.

When swapping coins from left to right: multiply by (1/Ask)
When swapping coins from right to left: multiply by Bid

With the three token pairs given in step 1, the algorithm for step 2 in pseudo code is then:
1. Assume first trade is from a_base to a_quote. Calculate the acquired coin by multiplying with the correct swap rate.
2. Check if the acquired coin (a_quote) is the same as that of b_base or b_quote. Swap this pair with the appropriate rate.
3. Now we have the coin b_base or b_quote. Check if that coin is the same as c_base or c_quote and perform swap. The acquired coin is now the same as the initial a_base.

Step 2 and 3 may be inverted, if the coin a_quote is found in pair c instead of b.