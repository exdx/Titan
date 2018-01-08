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
        self.interval = "5m"
        self.__thread = Thread(target=self.run)  # create thread for listener
        self.__jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.historical_loaded = False
        self.indicators = []
        self.strategies = []
        self.latest_candle = None
        self.PairID = random.randint(1, 100)
        ohlcv_functions.write_trade_pairs_to_db(self.PairID, self.base_currency, self.quote_currency)
        markets.append(self)
        self.__jobs.put(self.__load_historical)

    def run(self):
        """Start listener queue waiting for ticks"""
        self.__running = True
        while self.__running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                try:
                    print("Executing job: " + job.__name__ + " on " + self.exchange.id + " " + self.analysis_pair)
                    job()
                except Exception as e:
                    print(job.__name__ + " threw error:\n" + str(e))

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def tick(self):
        """Initiate pull of latest candle, ta calculations, and notify strategies"""
        if self.historical_loaded:
            self.__jobs.put(self.__pull_latest_candle)
            self.__jobs.put(self.__do_ta_calculations)
            self.__jobs.put(self.__tick_strategies)

    def __load_historical(self):
        """Load all historical candles to database"""
        print('Getting historical candles for market...')
        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
        for entry in data:
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry)
            self.latest_candle = entry
            self.__do_ta_calculations()
            print('Writing candle ' + str(entry[0]) + ' to database')
        self.historical_loaded = True
        print('Historical data has been loaded.')

    def __pull_latest_candle(self):
        """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
        print("Getting latest candle for " + self.exchange.id + " " + self.analysis_pair + " " + self.interval)
        latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]
        while latest_data == self.latest_candle:
            print('Candle already contained in DB, retrying...')
            time.sleep(self.exchange.rateLimit * 2 / 1000)
            latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)[-1]
        ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval,
                                                     latest_data)
        self.latest_candle = latest_data

    def __do_ta_calculations(self):
        for indicator in self.indicators:
            indicator.next_calculation()

    def __tick_strategies(self):
        for strategy in self.strategies:
            strategy.on_data()

    def apply_indicator(self, indicator):
        self.indicators.append(indicator)

    def apply_strategy(self, strategy):
        self.strategies.append(strategy)


def update_all_candles():
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
        market.tick()
