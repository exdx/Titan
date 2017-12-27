import ccxt
import time
import random
from core.database import ohlcv_functions
from threading import Thread
from queue import Queue

markets = []


class Market:
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.__thread = Thread(target=self.run)  # create thread for listener
        self.__jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.historical_loaded = False
        #self.load_historical("1m")
        self.load_historical("5m")
        self.indicators = []
        self.latest_candle = None
        self.PairID = random.randint(1,100)
        ohlcv_functions.write_trade_pairs_to_db(self.PairID,self.base_currency,self.quote_currency) #auto-write initialized market to DB with unique identifier
        markets.append(self)

    def run(self):
        """Start listener queue waiting for ticks"""
        while self.__running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                try:
                    print("Executing job: " + job.__name__ + " on " + self.exchange.id + " " + self.analysis_pair)
                    job()
                except Exception as e:
                    print(e)

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def load_historical(self, interval):
        """Queue action to load historical candles"""
        def do_load():
            """Load all historical candles to database"""
            print('Getting historical candles for market...')
            data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
            for entry in data:
                ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, entry)
                print('Writing candle ' + str(entry[0]) + ' to database')
            self.historical_loaded = True
            print('Historical data has been loaded.')
        if not self.historical_loaded:
            self.__jobs.put(do_load)

    def pull_latest_candle(self, interval):
        """Get the latest OHLCV candle for the market"""
        def do_pull():
            """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
            print("Getting latest candle for " + self.exchange.id + " " + self.analysis_pair + " " + interval)
            data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
            while ohlcv_functions.has_candle(data[-1], self.exchange.id, self.analysis_pair, interval):
                print('Candle already contained in DB, retrying...')
                time.sleep(self.exchange.rateLimit / 1000)
                data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, data[-1])
            self.latest_candle = data[-1]
        if self.historical_loaded:
            self.__jobs.put(do_pull)
            self.do_ta_calculations()

    def do_historical_ta_calculations(self):
        def do_historical_calculations():
            for indicator in self.indicators:
                indicator.calculate_historical()
        self.__jobs.put(do_historical_calculations)

    def do_ta_calculations(self):
        def do_calculations():
            for indicator in self.indicators:
                indicator.next_calculation()
        self.__jobs.put(do_calculations)

    def apply_indicator(self, indicator):
        self.indicators.append(indicator)


def update_all_candles(duration_minutes):
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
 #       market.pull_latest_candle("1m")
 #      if duration_minutes % 5 == 0:
        market.pull_latest_candle("5m")
