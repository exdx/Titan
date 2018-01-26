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
        self.api_key = None
        self.secret_key = None
        self.get_exchange_login()
        self.exchange = exchange({'apiKey': self.api_key, 'secret': self.secret_key, })
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.__thread = Thread(target=self.run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self.__running = True
        self.__thread.start()
        self.indicators = defaultdict(list)
        self.signals = []
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


    def _do_ta_calculations(self, interval):
        """Notify all indicators subscribed to the interval of a new candle"""
        for indicator in self.indicators[interval]:
            indicator.next_calculation()

    def apply_indicator(self, indicator):
        """Add indicator to list of indicators listening to market's candles"""
        self.indicators[indicator.interval].append(indicator)

    def get_exchange_login(self):
        """Put API Key and Secret into login-real.txt file on your local machine"""
        try:
            login_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'login-real.txt')
            with open(login_file) as f:
                data = f.read().splitlines()
            self.exchange.api_key = data[0]
            self.exchange.secret_key = data[1]
        except:
            print("Invalid login file")

    def get_wallet_balance(self):
        """Get wallet balance for quote currency"""
        try:
            print(self.exchange.fetch_balance())
            return self.exchange.fetch_balance()
        except BaseError:
            print("Not logged in properly")

    def get_best_bid(self):
        orderbook = self.exchange.fetch_order_book(self.analysis_pair)
        return orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None

    def get_best_ask(self):
        orderbook = self.exchange.fetch_order_book(self.analysis_pair)
        return orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None


def update_all_candles(interval):
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
        market.tick(interval)
