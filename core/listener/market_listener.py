import time
import ccxt
from core.database import ohlcv_functions


class Listener:
    def __init__(self, exchange, base_currency, quote_currency, interval):
        self.exchange = exchange
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.interval = interval
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.analysis_market = self.exchange.load_markets()[self.analysis_pair]
        self.wait_period = get_wait_period_from_interval(interval)
        self.interval = interval

        self.add_historical_candles()
        self.pull_ohlcv_data()

    def pull_ohlcv_data(self):
        if self.exchange.hasFetchOHLCV:
            while True:
                try:
                    data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                    if ohlcv_functions.has_candle(data[-1], self.exchange.id, self.analysis_pair, self.interval):
                        print('Candle already contained in DB, retrying...')
                        time.sleep(self.exchange.rateLimit / 1000)
                        continue
                    else:
                        print('Received latest candle')
                        self.add_candle(data[-1])  # add latest candle
                        print('Writing candle ' + str(data[-1][0]) + ' to database')
                        time.sleep(self.wait_period)
                except ccxt.BaseError as e:  # basic placeholder for error handling - fix later
                    print(e)

    def add_historical_candles(self):
        print('Getting historical candles')
        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
        for entry in data:
            self.add_candle(entry)
            print('Writing candle ' + str(entry[0]) + ' to database')

    def add_candle(self, candle_data):
        ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id,
                                                     self.analysis_pair,
                                                     self.interval,
                                                     candle_data)


def get_wait_period_from_interval(interval):
    if interval == "1m":
        return 59
    if interval == "5m":
        return 300
