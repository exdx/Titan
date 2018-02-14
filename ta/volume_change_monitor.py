from ta.base_indicator import BaseIndicator


class VolumeChangeMonitor(BaseIndicator):
    def __init__(self, market, interval):
        super(VolumeChangeMonitor, self).__init__(market, interval, 2)
        self.__previous_volume = 0
        self.value = None

    def next_calculation(self, candle):
        """get latest N candles from market, do calculation, write results to db"""
        new_volume = candle[5]
        if self.__previous_volume is not 0:
            self.value = round(100 * ((new_volume - self.__previous_volume) / self.__previous_volume), 2)  # calculate change in volume in percentage terms
        self.__previous_volume = new_volume

