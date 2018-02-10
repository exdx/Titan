from collections import defaultdict
from threading import Thread
from queue import Queue
from core.database import ohlcv_functions
from core.markets import ticker
from ccxt import BaseError
import ccxt
import logging
import time
from pubsub import pub
from threading import Lock

lock = Lock()
logger = logging.getLogger(__name__)

class MarketWatcher:
    """Active object that subscribes to a ticker of a specific interval and keeps track of OHLCV data
     A market watcher is instantiated with a trading pair (base, quote) and an interval
     It then subscribes to the ticker of that interval and calls for candles each time period
     It is responsible for syncing data with the DB and adding new candles
     Strategies that subscribe to the ticker will be given the new candles"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        exchange = getattr(ccxt, exchange)
        ticker.subscribe(self.tick, interval)
        self.analysis_pair = '{}/{}'.format(base_currency, quote_currency)
        self.exchange = exchange()
        self.interval = interval
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.topic = self.exchange.id + self.analysis_pair + self.interval
        self.__thread = Thread(target=self.__run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self.__running = False
        self.historical_synced = False
        self.latest_candle = None
        self.PairID = ohlcv_functions.write_trade_pairs_to_db(self.exchange.id, self.base_currency, self.quote_currency, self.interval)
        self.__thread.start()

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
                    print(e)
                    logger.error(job.__name__ + " threw error:\n" + str(e))

    def stop(self):
        """Stop listener queue"""
        self.__running = False

    def tick(self):
        """Queue a pull of the latest candle"""
        if self.historical_synced:
            self._jobs.put(lambda: self.__pull_latest_candle(self.interval))

    def sync_historical(self):
        """Queue loading of historical candles"""
        self._jobs.put(lambda: self.__sync_historical())

    def get_historical_candles(self):
        data = ohlcv_functions.get_all_candles(self.PairID)
        return data

    def __sync_historical(self):
        """Load all missing historical candles to database"""
        logger.info('Syncing market candles with DB...')
        latest_db_candle = ohlcv_functions.get_latest_candle(self.exchange.id, self.analysis_pair, self.interval)
        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
        if latest_db_candle is None:
            logger.info("No historical data for market, adding all available OHLCV data")
            for entry in data:
                ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry, self.PairID)
                print('Writing candle ' + str(entry[0]) + ' to database')
        else:
            for entry in data:
                if not latest_db_candle[10] >= entry[0]:
                    ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry, self.PairID)
                    print('Writing missing candle ' + str(entry[0]) + ' to database')
        self.historical_synced = True
        pub.sendMessage(self.topic + "historical")
        logger.info('Market data has been synced.')

    def __pull_latest_candle(self, interval):
        """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
        logger.info("Getting latest candle for " + self.exchange.id + " " + self.analysis_pair + " " + interval)
        print("Getting latest candle")
        latest_data = None
        try:
            latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
            while latest_data == self.latest_candle:
                print("retrying candle update")
                logger.info('Candle already contained in DB, retrying...')
                time.sleep(self.exchange.rateLimit * 2 / 1000)
                latest_data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-1]
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, latest_data, self.PairID)
        except Exception as e:
            print(e)
            logger.info("Timeout pulling latest candle, trying again")
            self.__pull_latest_candle(interval)
        self.latest_candle = latest_data
        pub.sendMessage(self.topic, candle=self.latest_candle)
        print("Sent message to " + self.topic)


lookup_list = defaultdict(MarketWatcher)


def get_market_watcher(exchange_id, base, quote, interval):
    """Return or create market watcher for the given analysis market"""
    topic = str(exchange_id + base + "/" + quote + interval)
    if topic not in lookup_list:
        lookup_list[topic] = MarketWatcher(exchange_id, base, quote, interval)
    return lookup_list[topic]


def subscribe_historical(exchange_id, base, quote, interval, callable):
    """Subscribe to a notification that is sent when historical data is loaded for the market given"""
    topic = str(exchange_id + base + "/" + quote + interval + "historical")
    pub.subscribe(callable, topic)


def subscribe(exchange_id, base, quote, interval, callable):
    """
    Enroll strategy to recieve new candles from a market
    :param exchange_id: string representing exchange i.e. 'bittrex'
    :param base: string represeting base i.e. ETH
    :param base: string represeting quote i.e. BTC
    :param interval: string representing interval i.e. '5m'
    :param callable: method to recieve new candle (must take candle as a param)
    :return: none
    """
    with lock:
        topic = str(exchange_id + base + "/" + quote + interval)
        get_market_watcher(exchange_id, base, quote, interval)
        print("Subscribing to " + topic)
        pub.subscribe(callable, topic)