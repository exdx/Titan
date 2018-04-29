
"""
Liquidity module
Purpose: Provide background liquidity statistics to trading platform in order to optimize trades and lower liquidity 
costs to end users

Liquidity costs are a function of the size of the order being filled, the inverse of the size of the liquidity on the 
chosen exchange, and the inverse of the intelligence of the liquidity provision in the system

Proposal: take larger trade sizes and split them up into multiple child orders to lower liquidity cost

"""

# liq_market = Market('binance', 'ETH', 'BTC', None)


import asyncio
import ccxt.async as ccxt

binance = ccxt.binance()
print(binance.fetch_markets())

async def print_binance_ethbtc_ticker():
    await binance.fetch_markets()

#asyncio.get_event_loop().run_until_complete(print_binance_ethbtc_ticker())
