import ccxt
from ccxt import BaseError
from core.listener import market_listener


class Market(BaseError):
    def __init__(self, exchange, base_currency, quote_currency):
        exchange = getattr(ccxt, exchange)
        self.exchange = exchange()
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.listener = market_listener.Listener(self.exchange, base_currency, quote_currency, "1m")
