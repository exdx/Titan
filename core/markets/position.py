"""Module to create, remove, and manage trades currently in play in running strategies"""
from core.markets.order import Order
import logging

logger = logging.getLogger(__name__)

positions = []


class Position:
    def __init__(self, market, amount, price):
        self.market = market
        self.amount = amount
        self.price = price

    def update(self):
        pass


class LongPosition(Position):
    """This class will handle a position's orders, stop losses, and exit/entry"""
    def __init__(self, market, amount, price, fixed_stoploss_percent, trailing_stoploss_percent, profit_target_percent):
        super().__init__(market, amount, price)
        self.is_open = False
        self.profit_target_percent = profit_target_percent
        self.trailing_stoploss_percent = self.price * trailing_stoploss_percent
        self.trailing_stoploss = self.calculate_trailing_stoploss()
        self.fixed_stoploss = price * fixed_stoploss_percent  # we can pass in an actual value to keep our fixed loss at
        self.profit_target = self.calculate_profit_target()
        self.initial_order = None

    def open(self):
        self.initial_order = self.market.limit_buy(self.amount, self.price)
        self.is_open = True

    def update(self):
        """Use this method to trigger position to check if profit target has been met, and re-set trailiing stop loss"""
        if not self.is_open:
            pass
        elif self.market.get_best_bid() < self.trailing_stoploss or \
                self.market.get_best_bid() < self.fixed_stoploss or \
                self.market.get_best_bid() >= self.profit_target:  # check price against last calculated trailing stoploss
            self.liquidate_position()
        # re-calculate trailing stoploss
        self.trailing_stoploss = self.calculate_trailing_stoploss()

    # calculate trailing stoploss based on percent (passed in as decimal for now)
    # for example if trailing_stoploss_percent = .97
    # and latest candle low is $100
    # the trailing_stoploss will be $97
    # using low for now, but we can change this
    def calculate_trailing_stoploss(self):
        return self.price * self.trailing_stoploss_percent

    # calculate profit target based on a percent (passed in as decimal for now)
    # if buy price was $100 and profit_target_percent = 1.03
    # profit target will be $103
    def calculate_profit_target(self):
        return self.price * self.profit_target_percent

    def update_trailing_stoploss(self):
        """Will use this method to actually create the order that will serve as the stop loss"""
        pass

    def liquidate_position(self):
        """Will use this method to actually create the order that liquidates the position"""
        logger.info("Liquidating long position of " + self.amount + " | " + self.market.analysis_pair)
        self.market.limit_sell(self.amount, self.market.get_best_bid())
        self.is_open = False


class ShortPosition(Position):
    """Short position is basically just to close out the order successfully ie liquidate_position"""
    def __init__(self, market, amount, price):
        super().__init__(market, amount, price)
        self.initial_order = None

    def open(self):
        self.initial_order = Order(self.market, "sell", "limit", self.amount, self.price)

    def confirm_sell_order(self):
        pass


def open_long_position(market, amount, price, fixed_stoploss_percent, trailing_stoploss_percent, profit_target_percent):
    position = LongPosition(market, amount, price, fixed_stoploss_percent, trailing_stoploss_percent, profit_target_percent)
    position.open()
    return position


def open_short_position(market, amount, price):
    position = ShortPosition(market, amount, price).open()
    position.open()
    return position


def calculate_transaction_fee(exchange, pair):
    return exchange.load_market(pair)['fee']


def calculate_drawdown():
    pass


