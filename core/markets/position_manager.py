"""Module to create, remove, and manage trades currently in play in running strategies"""

positions = []

def open_position(market, amount, price):
    positions.append(Position(market, Order(amount, price)))

class Position:
    """This class will handle a specific position's orders, stop losses, and exit/entry"""
    def __init__(self, market, order):
        self.market = market


class Order:
    """Class that represents an order"""
    def __init__(self, market, amount, price):
        self.market = market