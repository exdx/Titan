from collections import deque


class BaseIndicator:
    """Base class for indicators that handles the data, keeping it in RAM so no DB calls are needed"""
    def __init__(self, market, interval, periods):
        self.market = market
        self.interval = interval
        self.market.apply_indicator(self)
        self.periods = periods
