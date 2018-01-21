"""Module to create, remove, and manage trades currently in play in running strategies"""

from ccxt import OrderNotFound
from multiprocessing.pool import ThreadPool
from core.database import database


engine = database.engine
conn = engine.connect()

positions = []


class Order:
    """Class that represents an order. Order executes on instantiation by a thread pool"""
    def __init__(self, market, side, type, amount, price):
        self.market = market
        self.side = side
        self.type = type
        self.amount = amount
        self.price = price
        self.__order_receipt = None
        self.execute()

    def execute(self):
        if self.type == "limit":
            if self.side == "buy":
                self.__order_receipt = self.market.exchange.create_limit_buy_order(self.market.analysis_pair, self.amount, self.price)
                write_order_to_db(self.market.exchange.id, self.market.analysis_pair, 'long', self.amount, self.price)
            elif self.side == "sell":
                self.__order_receipt = self.market.exchange.create_limit_sell_order(self.market.analysis_pair, self.amount, self.price)
                write_order_to_db(self.market.exchange.id, self.market.analysis_pair, 'short', self.amount, self.price)
            else:
                print("Invalid order side: " + self.side + ", specify 'buy' or 'sell' ")
        elif self.type == "market":
            print("Market orders not available")
        else:
            print("Invalid order type: " + self.type + ", specify 'limit' or 'market' ")

    def get_id(self):
        return self.__order_receipt.get().id

    def cancel(self):
        try:
            self.market.exchange.cancel_order(self.get_id())
        except OrderNotFound:
            print("Order cannot be canceled. Has already been filled")

    def get_fill_price(self):
        order = self.market.exchange.fetchClosedOrders(symbol=self.market.analysis_pair)
        if order is None:
            print("Order not yet filled, cannot determine fill price")
        else:
            return order['price']


class Position:
    def __init__(self, market, amount, price):
        positions.append(self)
        self.market = market
        self.amount = amount
        self.price = price

    def update(self):
        pass


class LongPosition(Position):
    """This class will handle a position's orders, stop losses, and exit/entry"""
    def __init__(self, market, amount, price, fixed_stoploss, trailing_stoploss_percent, profit_target_percent):
        super().__init__(market, amount, price)
        self.is_open = False
        self.profit_target_percent = profit_target_percent
        self.trailing_stoploss_percent = self.price * trailing_stoploss_percent
        self.trailing_stoploss = self.calculate_trailing_stoploss()
        self.fixed_stoploss = fixed_stoploss  # we can pass in an actual value to keep our fixed loss at
        self.profit_target = self.calculate_profit_target()
        self.initial_order = None

    def open(self):
        self.initial_order = Order(self.market, "buy", "limit", self.amount, self.price)
        self.is_open = True

    def update(self):
        """Use this method to trigger position to check if profit target has been met, and re-set trailiing stop loss"""
        if self.market.latest_candle[3] < self.trailing_stoploss or\
            self.market.latest_candle[3] < self.fixed_stoploss or\
            self.market.get_latest_bid() >= self.profit_target:  # check price against last calculated trailing stoploss
                self.liquidate_position()
        # re-calculate trailing stoploss
        self.trailing_stoploss = self.calculate_trailing_stoploss()

    # calculate trailing stoploss based on percent (passed in as decimal for now)
    # for example if trailing_stoploss_percent = .97
    # and latest candle low is $100
    # the trailing_stoploss will be $97
    # using low for now, but we can change this
    def calculate_trailing_stoploss(self):
        return self.market.latest_candle[3] * self.trailing_stoploss_percent

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
        open_short_position(self.market, self.amount, self.market.get_latest_bid())
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


def update_all_positions():
    for position in positions:
        position.update()


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


def write_order_to_db(exchange, pair, position, amount, price):
    ins = database.TradingPositions.insert().values(Exchange=exchange, Pair=pair, Position=position, Amount=amount, Price=price)
    conn.execute(ins)
    print("Wrote open order to DB...")