import time
import ccxt
from core.database import ohlcv_functions



class Market(ccxt.BaseError):
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

                        ##clear DB
                        #clear_ohlcv_table()
                        #print('Clearing old table')
                        ##clear for debug, do not want to fill db with useless repeated data from debugging

                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
                        for entry in data:


                            ##debugging this method
                            #has_candle(entry, self.exchange.id, self.interval)


                            candle_count += 1
                            insert_data_into_ohlcv_table(candle_count,
                                                         self.exchange.id,
                                                         self.interval,
                                                         entry)

                            print('Writing candle ' + str(candle_count) + ' to database')
                        time.sleep(self.wait_period)
                    else:
                        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]
                        while has_candle(data, self.exchange.id, self.interval):  # be sure not to add a duplicate candle
                            print('Candle already contained in DB, waiting one second to retry...')
                            time.sleep(1)
                            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]  # check for later candle
                        candle_count += 1
                        insert_data_into_ohlcv_table(candle_count,
                                                     self.exchange.id,
                                                     self.interval,
                                                     entry)  # add latest candle

                        print('Received latest candle')

                        print('Writing candle ' + str(candle_count) + ' to database')
                        time.sleep(self.wait_period)
                except ccxt.BaseError as e: #basic placeholder for error handling - fix later
                    print(e)