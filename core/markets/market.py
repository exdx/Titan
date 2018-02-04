import ccxt
import logging
import os
from core.markets import order
from collections import defaultdict
from core.markets import market_watcher
from ccxt import BaseError


logger = logging.getLogger(__name__)

markets = []


class Market:
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency, strategy):
        exchange = getattr(ccxt, exchange)
        self.strategy = strategy
        self.api_key = None
        self.secret_key = None
        self.get_exchange_login()
        self.exchange = exchange({'apiKey': self.api_key, 'secret': self.secret_key, })
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.signals = []
        self.ohlcv_id = defaultdict(int)
        self.indicators = defaultdict(list)
        self.candles = defaultdict(list)
        self.latest_candle = defaultdict(list)
        markets.append(self)

    def update(self, interval, candle):
        """Notify all indicators subscribed to the interval of a new candle"""
        self.latest_candle[interval] = candle
        self.candles[interval].append(candle)
        self.do_ta_calculations(interval, candle)

    def do_ta_calculations(self, interval, candle):
        """update TA indicators applied to market"""
        for indicator in self.indicators[interval]:
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
            logger.error("Invalid login file")

    def limit_buy(self, quantity, price):
        try:
            self.strategy.send_message("Executed buy of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            return order.Order(self, "buy", "limit", quantity, price)
        except BaseError:
            self.strategy.send_message("Error creating buy order")
            logger.error("Error creating buy order")

    def limit_sell(self, quantity, price):
        try:
            self.strategy.send_message("Executed sell of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            return order.Order(self, "sell", "limit", quantity, price)
        except BaseError:
            self.strategy.send_message("Error creating sell order")
            logger.error("Error creating sell order")

    def get_wallet_balance(self):
        """Get wallet balance for quote currency"""
        try:
            logger.info(self.exchange.fetch_balance())
            return self.exchange.fetch_balance()
        except BaseError:
            logger.error("Not logged in properly")

    def get_best_bid(self):
        orderbook = self.exchange.fetch_order_book(self.analysis_pair)
        return orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None

    def get_best_ask(self):
        orderbook = self.exchange.fetch_order_book(self.analysis_pair)
        return orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None

    def get_historical_candles(self, interval, candle_limit=None):
        if len(self.candles[interval]) == 0:
            self.candles[interval] = market_watcher.get_market_watcher(self.exchange.id, self.base_currency, self.quote_currency, interval).get_historical_candles()
        if candle_limit is None:
            return self.candles[interval]
        else:
            return self.candles[interval][-candle_limit:]