import time
import ccxt
from ccxt import BaseError
from core.database import ohlcv_functions



class Market(BaseError):
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
            latest_candle = ohlcv_functions.get_latest_candle_id(self.exchange.id, self.interval)
            candle_count = latest_candle if (latest_candle != None) else 0

            while True:
                try:
                    if candle_count == 0:  # check to see if historical candles have been pulled
                        print('Pulling latest batch of candles')
                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                        for entry in data:
                            candle_count += 1
                            ohlcv_functions.insert_data_into_ohlcv_table(candle_count,
                                                         self.exchange.id,
                                                         self.interval,
                                                         entry)

                            print('Writing candle ' + str(candle_count) + ' to database')
                        time.sleep(self.wait_period)
                    else:
                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                        if ohlcv_functions.has_candle(data[-1], self.exchange.id, self.interval):  # be sure not to add a duplicate candle
                            print('Candle already contained in DB, waiting one second to retry...')
                            time.sleep(self.exchange.rateLimit/1000)
                        else:
                            candle_count += 1
                            ohlcv_functions.insert_data_into_ohlcv_table(candle_count,
                                                         self.exchange.id,
                                                         self.interval,
                                                         data[-1])  # add latest candle

                            print('Received latest candle')

                            print('Writing candle ' + str(candle_count) + ' to database')
                            time.sleep(self.wait_period)
                except ccxt.BaseError as e: #basic placeholder for error handling - fix later
                    print(e)