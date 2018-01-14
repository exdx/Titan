"""Module to create, remove, and manage trades currently in play in running strategies"""
import json
from ccxt import BaseError

positions = []


class Order:
    """Class that represents an order"""
    def __init__(self,  position, amount, price):
        self.position = position
        self.amount = amount
        self.price = price


class Position(Order):
    """This class will handle a specific position's orders, stop losses, and exit/entry"""
    def __init__(self, position, amount, price, fixed_stoploss, trailing_stop_loss):
        super.__init__(position, amount, price)
        self.fixed_stoploss = fixed_stoploss
        self.trailing_stop_loss = trailing_stop_loss
        self.profit_target = 3

    def calculate_stoploss(self, latest_candle):
        if self.position == 'long':
            self.fixed_stoploss = self.price * 0.99
            self.trailing_stop_loss = latest_candle * 0.997  # latest candle in the future - needs logic
        elif self.position == 'short':
            pass

    def calculate_profit_target(self, exchange, pair, amount, buy_price, sell_price):
        if self.position == 'long':
            self. proceeds = amount * ((create_limit_sell_order(exchange, pair, amount, buy_price))-create_limit_sell_order(exchange, pair, amount, sell_price))
            if self.position == 'short':
                pass


def open_position(market, amount, position, price):
    positions.append(Position(market, Order(position, amount, price)))


def create_limit_buy_order(exchange, pair, amount, buy_price):
    try:
        buy_order = exchange.createLimitBuyOrder(pair, amount, buy_price)
        buy_order()
        open_position(exchange, amount, 'long', buy_price)
        json.loads(buy_order)
        return buy_order['price']

    except BaseError:
        print("Order did not go through")


def create_limit_sell_order(exchange, pair, amount, sell_price):
    try:
        sell_order = exchange.createLimitSellOrder(pair, amount, sell_price)
        sell_order()
        open_position(exchange, amount, 'short', sell_price)
        json.loads(sell_order)
        return sell_order['price']

    except BaseError:
        print("Order did not go through")


def get_latest_bid(exchange):
    latest_bid = exchange.fetch_ticker(exchange.pair)['bid']
    return latest_bid


def get_latest_ask(exchange):
    latest_ask = exchange.fetch_ticker(exchange.pair)['ask']
    return latest_ask


def calculate_transaction_fee(exchange, pair):
    return exchange.load_market(pair)['fee']


def calculate_drawdown():
    pass
