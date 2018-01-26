from collections import defaultdict
from threading import Thread
from queue import Queue
from core.database import ohlcv_functions
import ccxt
import random
import time

market_watchers = defaultdict(dict)


def update_all(interval):
    for key, value in market_watchers[interval].items():
        value.tick()


def subscribe(interval, exchange_id):
    return market_watchers[interval][exchange_id]


class MarketWatcher:
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.interval = interval
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.__thread = Thread(target=self.run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.historical_synced = False
        self.signals = []
        self.latest_candle = defaultdict(list)
        self.PairID = random.randint(1, 100)
        ohlcv_functions.write_trade_pairs_to_db(self.PairID, self.base_currency, self.quote_currency)

    def run(self):
        """Start listener queue waiting for ticks"""
        self.__running = True
        while self.__running:
            if not self._jobs.empty():
                job = self._jobs.get()
                try:
                    print("Executing job: " + job.__name__ + " on " + self.exchange.id + " " + self.analysis_pair)
                    job()
                except Exception as e:
                    print(job.__name__ + " threw error:\n" + str(e))

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def tick(self, interval):
        """Initiate pull of latest candle, ta calculations, and notify strategies"""
        if self.historical_synced:
            self._jobs.put(lambda: self._pull_latest_candle(interval))

    def sync_historical(self, interval):
        """Queue loading of historical candles"""
        self._jobs.put(lambda: self._sync_historical(interval))

    def _sync_historical(self, interval):
        """Load all historical candles to database
        This method overrides the load historical of the base class as it is a blocking method (not added to thread queue)
        and ticks applied strategies on historical data"""
        print('Getting historical candles for market...')
        data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
        for entry in data:
            if ohlcv_functions.get_latest_candle(self.exchange.id, self.analysis_pair, interval)[10] >= entry[0]:
                ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, entry)
                self.latest_candle[interval] = entry
                print('Writing candle ' + str(entry[0]) + ' to database')
        self.historical_synced = True
        print('Historical data has been loaded.')

    def _pull_latest_candle(self, interval):
        """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
        print("Getting latest candle for " + self.exchange.id + " " + self.analysis_pair + " " + interval)
        latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
        while latest_data == self.latest_candle[interval]:
            print('Candle already contained in DB, retrying...')
            time.sleep(self.exchange.rateLimit * 2 / 1000)
            latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
        ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval,
                                                     latest_data)
        self.latest_candle[interval] = latest_data
