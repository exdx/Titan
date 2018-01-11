"""Module to create, remove, and manage trades currently in play in running strategies"""
import ccxt
from ccxt import BaseError
import os

positions = []

def open_position(market, amount, position, price):
    positions.append(Position(market, Order(position, amount, price)))

class Order:
    """Class that represents an order"""
    def __init__(self, exchange, pair, amount, price, position='long'):
        exchange = getattr(ccxt, exchange)
        self.get_exchange_login()
        self.exchange = exchange({'apiKey': self.api_key, 'secret': self.secret_key, })
        self.pair = pair
        self.position = position
        self.amount = amount
        self.price = price

    def pull_orderbook(self):
        """Pulls orderbook and finds best ask and bid prices to trade at the time"""
        orderbook = self.exchange.fetch_order_book(self.pair)
        self.best_bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        self.best_ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        self.spread = (self.best_ask - self.best_bid) if (self.best_bid and self.best_ask) else None
        session = (self.exchange.id, 'market price', {'best bid': self.best_bid, 'best ask': self.best_ask, 'spread': self.spread})
        print(session)

    def get_exchange_login(self):
        """Put API Key and Secret into login-real.txt file on your local machine"""
        login_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'login-real.txt')
        with open(login_file) as f:
            data = f.read().splitlines()
        self.api_key = data[0]
        self.secret_key = data[1]

    def get_wallet_balance(self):
        try:
            print(self.exchange.fetch_balance())
            return self.exchange.fetch_balance()
        except BaseError:
            print("Not logged in properly")

    def create_limit_buy_order(self):
        try:
            self.exchange.createLimitBuyOrder(self.pair, self.amount, self.price)
            open_position(self.exchange, self.amount, self.position, self.price)
        except BaseError:
            print("Order did not go through")

    def create_limit_sell_order(self):
        try:
            self.exchange.createLimitSellOrder(self.pair, self.amount, self.price)
            open_position(self.exchange, self.amount, self.position, self.price)
        except BaseError:
            print("Order did not go through")


class Position(Order):
    """This class will handle a specific position's orders, stop losses, and exit/entry"""
    def __init__(self, market, order):
        super.__init__(market, order)




test_object = Order('bittrex','ETH/BTC',1,0.004)
test_object.pull_orderbook()
test_object.get_exchange_login()
test_object.get_wallet_balance()