import datetime
import time
import logging
from ccxt import OrderNotFound
from core.database import database


logger = logging.getLogger(__name__)

engine = database.engine
conn = engine.connect()


class Order:
    """Class that represents an order. Order executes on instantiation by a thread pool"""
    def __init__(self, market, side, type, amount, price):
        self.market = market
        self.side = side
        self.type = type
        self.amount = amount
        self.price = price
        self.__order_receipt = None
        logger.info("Opening " + side + " order of " + amount + " " + self.market.base_currency)
        self.execute()

    def execute(self):
        if self.type == "limit":
            if self.side == "buy":
                self.__order_receipt = self.market.exchange.create_limit_buy_order(self.market.analysis_pair, self.amount, self.price)
                write_order_to_db(self.market.exchange.id, self.market.analysis_pair, 'long', self.amount, self.price, "live")
            elif self.side == "sell":
                self.__order_receipt = self.market.exchange.create_limit_sell_order(self.market.analysis_pair, self.amount, self.price)
                write_order_to_db(self.market.exchange.id, self.market.analysis_pair, 'short', self.amount, self.price, "live")
            else:
                logger.error("Invalid order side: " + self.side + ", specify 'buy' or 'sell' ")
        elif self.type == "market":
            logger.error("Market orders not available")
        else:
            logger.error("Invalid order type: " + self.type + ", specify 'limit' or 'market' ")

    def get_id(self):
        return self.__order_receipt.get().id

    def cancel(self):
        try:
            self.market.exchange.cancel_order(self.get_id())
        except OrderNotFound:
            logger.error("Order cannot be canceled. Has already been filled")

    def is_open(self):
        return self.market.exchange.fetch_order(self.get_id())['remaining'] > 0

    def get_status(self):
        return self.market.exchange.fetch_order(self.get_id())['status']

    def get_amount_filled(self):
        return self.market.exchange.fetch_order(self.get_id())['filled']

    def get_amount_remaining(self):
        return self.market.exchange.fetch_order(self.get_id())['remaining']


def write_order_to_db(exchange, pair, position, amount, price, simulated):
    with database.lock:
        ins = database.TradingOrders.insert().values(Timestamp=get_timestamp(), Exchange=exchange, Pair=pair, Position=position, Amount=amount, Price=price, Simulated=simulated)
        conn.execute(ins)
        logger.info("Wrote open order to DB...")


def get_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
