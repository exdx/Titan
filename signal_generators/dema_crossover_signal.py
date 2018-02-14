from ta.exponential_moving_average import ExponentialMovingAverage
from signal_generators.base_signal_generator import BaseSignalGenerator


class DEMACrossoverSignal(BaseSignalGenerator):
    """"This signal generator is a copy of the DEMA strategy example used in gekko
    This strategy is similar to the sma_crossover_signal except is is simpler in that it does not worry about caching candles
    ...it simply signals true when FMA > SMA and false whe SMA > FMA at an amount greater than the threshold"""
    def __init__(self, market, interval, ema_short, ema_long, strategy):
        super().__init__(market, interval, strategy)
        self.fma = ExponentialMovingAverage(self.market, interval, ema_short)
        self.sma = ExponentialMovingAverage(self.market, interval, ema_long)
        self.threshold = .025

    def check_condition(self, new_candle):
        """will run every time a new candle is pulled"""
        self.strategy.print_message("GETTING DEMA CROSSOVER SIGNAL")
        if (self.sma.value is not None) & (self.fma.value is not None):
            self.strategy.print_message("SMA: " + str(self.sma.value))
            self.strategy.print_message("FMA: " + str(self.fma.value))
            if (self.fma.value - self.sma.value) > self.threshold:
                self.strategy.print_message("Currently in up-trend. Buy signal TRUE")
                return True
        return False
