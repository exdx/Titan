from collections import deque


class BaseIndicator:
    """Base class for indicators that handles the data, keeping it in RAM so no DB calls are needed"""
    def __init__(self, market, interval, periods):
        self.market = market
        self.market.indicators.append(self)
        self.interval = interval
        self.periods = periods
        self.dataset = deque(maxlen=periods)

    def update_dataset(self, candle):
        if len(self.dataset) == self.periods:
            self.dataset.popleft()
        self.dataset.append(candle)
