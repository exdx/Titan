from collections import defaultdict
from threading import Thread
from queue import Queue
from core.database import ohlcv_functions
from core.markets import ticker
from ccxt import BaseError
from ccxt.base.errors import RequestTimeout
import ccxt
import random
import time
from pubsub import pub
from threading import Lock

lock = Lock()

class MarketWatcher:
    """Active object that subscribes to a ticker of a specific interval and keeps track of OHLCV data
    A market watcher is instantiated with a trading pair (base, quote) and an interval
    It then subscribes to the ticker of that interval and calls for candles each time period
    It is responsible for syncing data with the DB and adding new candles
    Strategies that subscribe to the ticker will be given the new candles"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        """Creates and starts the thread, ccxt exchange object, and initializes attributes """
        exchange = getattr(ccxt, exchange)
        ticker.start_ticker(interval)
        self.analysis_pair = '{}/{}'.format(base_currency, quote_currency)
        self.exchange = exchange()
        self.interval = interval
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.topic = str(self.exchange.id + self.analysis_pair + self.interval)
        self.__thread = Thread(target=self.__run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self.__running = False
        self.live = False
        self.latest_candle = None
        self.__thread.start()
        pub.subscribe(self.tick, "tick" + interval)


    def __run(self):
        """Start listener queue waiting for ticks"""
        self.__running = True
        self.sync_historical()
        while self.__running:
            if not self._jobs.empty():
                job = self._jobs.get()
                try:
                    job()
                except Exception as e:
                    print(job.__name__ + " threw error:\n" + str(e))

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def tick(self):
        """Initiate a pull of latest candle"""
        if self.live:
            self._jobs.put(lambda: self._pull_latest_candle(self.interval))

    def sync_historical(self):
        """Queue loading of missing historical candles"""
        self._jobs.put(lambda: self.__sync_historical())

    def __sync_historical(self):
        """Load all missing historical candles to database
        and ticks applied strategies on historical data"""
        try:
            print('Syncing market candles with DB...')
            latest_db_candle = ohlcv_functions.get_latest_candle(self.exchange.id, self.analysis_pair, self.interval)
            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
            if latest_db_candle is None:
                print("No historical data for market, adding all available OHLCV data")
                for entry in data:
                    ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry)
                    print('Writing candle ' + str(entry[0]) + ' to database')
            else:
                for entry in data:
                    if not latest_db_candle[10] >= entry[0]:
                        ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry)
                        print('Writing missing candle ' + str(entry[0]) + ' to database')
            self.live = True
            pub.sendMessage(self.topic + "historical")
            print('Market data has been synced.')
        except:
            self.__sync_historical()

    def _pull_latest_candle(self, interval):
        """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
        print("Getting latest candle for " + self.exchange.id + " " + self.analysis_pair + " " + interval)
        try:
            latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
            while latest_data == self.latest_candle:
                print('Candle already contained in DB, retrying...')
                time.sleep(self.exchange.rateLimit * 2 / 1000)
                latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, latest_data)
            self.latest_candle = latest_data
            pub.sendMessage(self.topic, candle=self.latest_candle)
        except BaseError:
            print("Timeout pulling latest candle, trying again")
            self._pull_latest_candle(interval)


lookup_list = defaultdict(MarketWatcher)


def subscribe_historical(exchange_id, base, quote, interval, callable):
    """Subscribe to a notification that is sent when historical data is loaded for the market given"""
    topic = str(exchange_id + base + "/" + quote + interval + "historical")
    pub.subscribe(callable, topic)


def subscribe(exchange_id, base, quote, interval, callable):
    """
    Enroll a strategy to recieve new candles from a market
    :param exchange_id: string representing exchange i.e. 'bittrex'
    :param base: string represeting base i.e. ETH
    :param base: string represeting quote i.e. BTC
    :param interval: string representing interval i.e. '5m'
    :param callable: method to recieve new candle (must take candle as a param)
    :return: none
    """
    with lock:
        topic = str(exchange_id + base + "/" + quote + interval)
        pub.subscribe(callable, topic)
        if topic not in lookup_list:
            lookup_list[topic] = MarketWatcher(exchange_id, base, quote, interval)