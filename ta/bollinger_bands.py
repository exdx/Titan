from pyti.bollinger_bands import upper_bollinger_band as calc_upper_bband
from pyti.bollinger_bands import lower_bollinger_band as calc_lower_bband
from pyti.bollinger_bands import middle_bollinger_band as calc_middle_bband
from pyti.bollinger_bands import bandwidth as calc_bandwidth
from pyti.bollinger_bands import bb_range as calc_range
from ta.base_indicator import BaseIndicator


class BollingerBands(BaseIndicator):
    def __init__(self, market, interval, periods):
        super().__init__(market, interval, periods)
        self.value = None
        self.upper_band = None
        self.middle_band = None
        self.lower_band = None
        self.bandwidth = None
        self.range = None

    def next_calculation(self, candle):
        """get latest candles from market, do calculation, write results to db"""
        dataset = self.market.candles[self.interval]            # save reference of market candles for read-ability
        if len(dataset) >= self.periods:                        # check that enough market candles are available for calculation
            data_window = dataset[-self.periods:]               # take slice of correct number of candles
            data = list(c[4] for c in data_window)              # take list of close values from candles
            self.upper_band = round(calc_upper_bband(data, self.periods)[-1], 6)  # update upper band
            self.middle_band = round(calc_middle_bband(data, self.periods)[-1], 6)  # update middle band
            self.lower_band = round(calc_lower_bband(data, self.periods)[-1], 6)  # update lower band
            self.bandwidth = round(calc_bandwidth(data, self.periods)[-1], 6)  # update bandwidth
            self.range = round(calc_range(data, self.periods)[-1], 6)  # update range
