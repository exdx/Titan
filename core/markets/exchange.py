import ccxt
from ccxt import BaseError
from core.listener import market_listener


class Market(BaseError):
    """Initialize core Market object that details the exchange, trade pair, and interval being considered in each case"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.interval = interval
        self.listener = market_listener.Listener(self.exchange, self.base_currency, self.quote_currency, self.interval)
