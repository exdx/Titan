#Create database to write bitcoin price data into

import time
import ccxt

#make class that holds all subject data
class Exchange():
    def __init__(self, exchange, base_currency, quote_currency):
        self.exchange = ccxt.bittrex()
        self.markets  = self.exchange.load_markets()
        self.symbols = self.exchange.symbols
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def pull_OHLCV_data(self, interval):
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.analysis_market = self.exchange.markets[self.analysis_pair]
        self.interval = interval

        if self.exchange.hasFetchOHLCV:
            while True:
                time.sleep(self.exchange.rateLimit / 1000)  # time.sleep wants seconds
                print(self.analysis_pair, self.exchange.fetch_ohlcv(self.analysis_pair, self.interval))


ETH_BTC_Exchange = Exchange('bittrex','ETH','BTC')
ETH_BTC_Exchange.pull_OHLCV_data('1m')
