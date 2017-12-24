import ccxt
import time
from core.database import ohlcv_functions
from threading import Thread
from queue import Queue

markets = []


class Market:
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.interval = interval
        self.__thread = Thread(target=self.run)  # create thread for listener
        self.__jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.historical_loaded = False
        self.load_historical()
        self.indicators = []
        self.latest_candle = None
        markets.append(self)

    def run(self):
        """Start listener queue waiting for ticks"""
        while self.__running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                try:
                    print("Executing job: " + str(job) + " on " + self.exchange.id + " " + self.analysis_pair + " " + self.interval)
                    job()
                except Exception as e:
                    print(e)

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def load_historical(self):
        """Queue action to load historical candles"""
        def do_load():
            """Load all historical candles to database"""
            print('Getting historical candles for market...')
            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
            for entry in data:
                ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry)
                print('Writing candle ' + str(entry[0]) + ' to database')
            self.__historical_loaded = True
        if not self.historical_loaded:
            self.__jobs.put(do_load)
            #self.__jobs.put()

    def pull_latest_candle(self):
        """Get the latest OHLCV candle for the market"""
        def do_pull():
            """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
            while ohlcv_functions.has_candle(data[-1], self.exchange.id, self.analysis_pair, self.interval):
                print('Candle already contained in DB, retrying...')
                time.sleep(self.exchange.rateLimit / 1000)
                data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, data[-1])
            self.latest_candle = data[-1]
        if self.historical_loaded:
            self.__jobs.put(do_pull)
            self.__jobs.put(self.do_ta_calculations)

    def do_historical_ta_calculations(self):
        for indicator in self.indicators:
            indicator.calculate_historical()

    def do_ta_calculations(self):
        for indicator in self.indicators:
            indicator.next_calculation()

    def apply_indicator(self, indicator):
        self.indicators.append(indicator)

    def __get_wait_period_from_interval(interval):
        """Convert given interval to integer wait period (will be more helpful when we support different intervals)"""
        if interval == "1m":
            return 59
        if interval == "5m":
            return 299


def update_all_candles():
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
        market.pull_latest_candle()
