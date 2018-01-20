import ccxt
import time
import random
import os
from collections import defaultdict
from core.database import ohlcv_functions
from threading import Thread
from queue import Queue
from ccxt import BaseError

markets = []


class Market:
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency):
        exchange = getattr(ccxt, exchange)
        self.get_exchange_login()
        self.exchange = exchange({'apiKey': self.api_key, 'secret': self.secret_key, })
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.__thread = Thread(target=self.run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.historical_loaded = False
        self.indicators = defaultdict(list)
        self.strategies = []
        self.latest_candle = defaultdict(list)
        self.PairID = random.randint(1, 100)
        ohlcv_functions.write_trade_pairs_to_db(self.PairID, self.base_currency, self.quote_currency)
        markets.append(self)

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
        if self.historical_loaded:
            self._jobs.put(lambda: self._pull_latest_candle(interval))
            self._jobs.put(lambda: self._do_ta_calculations(interval))
            self._jobs.put(self._tick_strategies)

    def load_historical(self, interval):
        """Queue loading of historical candles"""
        self._jobs.put(lambda: self._load_historical(interval))

    def _load_historical(self, interval):
        """Load all historical candles to database
        This method overrides the load historical of the base class as it is a blocking method (not added to thread queue)
        and ticks applied strategies on historical data"""
        print('Getting historical candles for market...')
        data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
        for entry in data:
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, interval, entry)
            self.latest_candle[interval] = entry
            self._do_ta_calculations(interval)
            print('Writing candle ' + str(entry[0]) + ' to database')
        self.historical_loaded = True
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

    def _do_ta_calculations(self, interval):
        """Notify all indicators subscribed to the interval of a new candle"""
        for indicator in self.indicators[interval]:
            indicator.next_calculation()

    def _tick_strategies(self):
        """Notify strategies of a new candle"""
        for strategy in self.strategies:
            strategy.on_data()

    def apply_indicator(self, indicator):
        """Add indicator to list of indicators listening to market's candles"""
        self.indicators[indicator.interval].append(indicator)

    def apply_strategy(self, strategy):
        """Add strategy to list of strategies listening to market's candles"""
        self.strategies.append(strategy)

    def get_exchange_login(self):
        """Put API Key and Secret into login-real.txt file on your local machine"""
        login_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'login-real.txt')
        with open(login_file) as f:
            data = f.read().splitlines()
        self.api_key = data[0]
        self.secret_key = data[1]

    def get_wallet_balance(self):
        """Get wallet balance for quote currency"""
        try:
            print(self.exchange.fetch_balance())
            return self.exchange.fetch_balance()
        except BaseError:
            print("Not logged in properly")


def update_all_candles(interval):
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
        market.tick(interval)
