import time
import ccxt
from ccxt import BaseError
from price_database_functions import *

#make class that holds all subject data
class Exchange(BaseError):
    def __init__(self, exchange, base_currency, quote_currency):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.markets  = self.exchange.load_markets()
        self.symbols = self.exchange.symbols
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def pull_OHLCV_data(self, wait_period, interval):
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.analysis_market = self.exchange.markets[self.analysis_pair]
        self.wait_period = wait_period
        self.interval = interval

        if self.exchange.hasFetchOHLCV:
            candle_count = 0  # keep track of number of candles for life of object
            while True:
                try:
                    if candle_count == 0:  # check to see if historical candles have been pulled
                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                        for entry in data:
                            insert_data_into_ohlcv_table(entry)
                            candle_count += 1
                        time.sleep(self.wait_period)
                    else:
                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]
                        while has_candle(data, self.exchange.id, self.interval):  # be sure not to add a duplicate candle
                            time.sleep(1)
                            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]  # check for later candle
                        insert_data_into_ohlcv_table(data)  # add latest candle
                        candle_count += 1
                        time.sleep(self.wait_period)
                except ccxt.BaseError as e: #basic placeholder for error handling - fix later
                    print(e)






