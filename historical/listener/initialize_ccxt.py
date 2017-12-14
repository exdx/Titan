import time
import ccxt
from ccxt import BaseError
from price_database_functions import insert_data_into_ohlcv_table

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
            while True:
                try:
                    data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                    for entry in data:
                        insert_data_into_ohlcv_table(entry)
                    time.sleep(self.wait_period)
                except ccxt.BaseError as e: #basic placeholder for error handling - fix later
                    print(e)






