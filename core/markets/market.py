import ccxt
import time
import random
import os
from core.markets import order
from collections import defaultdict
from core.database import ohlcv_functions

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
        self.indicators = defaultdict(list)
        self.signals = []
        self.latest_candle = defaultdict(list)
        self.PairID = random.randint(1, 100)
        ohlcv_functions.write_trade_pairs_to_db(self.PairID, self.base_currency, self.quote_currency)
        markets.append(self)

    def update(self, interval, candle):
        """Notify all indicators subscribed to the interval of a new candle"""
        self.latest_candle[interval] = candle
        self.do_ta_calculations(interval, candle)

    def do_ta_calculations(self, interval, candle):
        """update TA indicators applied to market"""
        for indicator in self.indicators[interval]:
            indicator.next_calculation(candle)

    def do_historical_ta_calculations(self, interval, candle_limit=None):
        if candle_limit is None:
            data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)
        else:
            data = self.exchange.fetch_ohlcv(self.analysis_pair, interval)[-candle_limit:]
        for indicator in self.indicators[interval]:
            for candle in data:
                indicator.next_calculation(candle)

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

    def limit_buy(self, quantity, price):
        try:
            print()
            print("Executed buy of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            print()
            return order.Order(self, "buy", "limit", quantity, price)
        except BaseError:
            print("Error creating buy order")

    def limit_sell(self, quantity, price):
        try:
            print()
            print("Executed sell of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            print()
            return order.Order(self, "sell", "limit", quantity, price)
        except BaseError:
            print("Error creating sell order")

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

    # this method slows everything down big time
    # looking for solutions (a 5000 entry query should not take multiple seconds to iterate)
    # https://stackoverflow.com/questions/9402033/python-is-slow-when-iterating-over-a-large-list
    def get_historical_candles(self, interval, candle_limit=None):
        if candle_limit is None:
            data = ohlcv_functions.get_all_candles(self.exchange.id, self.analysis_pair, interval)
        else:
            data = ohlcv_functions.get_latest_N_candles(self.exchange.id, self.analysis_pair, interval, candle_limit)
        return [[entry[10], entry[4], entry[5], entry[6], entry[7], entry[8]] for entry in data]


def update_all_candles(interval):
    """Tell all instantiated markets to pull their latest candle"""
    for market in markets:
        market.tick(interval)
