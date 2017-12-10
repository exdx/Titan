#Create database to write bitcoin price data into

import time
import ccxt
import sqlite3
import sqlalchemy

#initialize settings for the market we are interested in
exchange = ccxt.bittrex()
markets = exchange.load_markets()
symbols = exchange.symbols
analysis_pair = 'ETH/BTC'
analysis_market = exchange.markets[analysis_pair]

#pull OHLCV data
if exchange.hasFetchOHLCV:
    while True:
        time.sleep(exchange.rateLimit / 1000) # time.sleep wants seconds
        print(analysis_pair, exchange.fetch_ohlcv (analysis_pair, '1m')) # one min

