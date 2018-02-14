from pyti.simple_moving_average import simple_moving_average as sma
from ta.base_indicator import BaseIndicator


class SimpleMovingAverage(BaseIndicator):
    def __init__(self, market, interval, periods):
        super().__init__(market, interval, periods)
        self.value = None

    def next_calculation(self, candle):
        """get latest candles from market, do calculation, write results to db"""
        dataset = self.market.candles[self.interval]            # save reference of market candles for read-ability
        if len(dataset) >= self.periods:                        # check that enough market candles are available for calculation
            data_window = dataset[-self.periods:]               # take slice of correct number of candles
            data = list(c[4] for c in data_window)              # take list of close values from candles
            self.value = round(sma(data, self.periods)[-1], 6)  # update current value
