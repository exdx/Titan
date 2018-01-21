import core.database
from ta import simple_moving_average
from ta import volume_change_monitor
from signal_generators.base_signal_generator import BaseSignalGenerator


class SmaCrossoverSignal(BaseSignalGenerator):
    def __init__(self, market, sma_short, sma_long, interval):
        """here is where you determine your values to keep track of, etc"""
        super().__init__()
        self.market = market
        self.market.load_historical("5m")
        self.fma = simple_moving_average.SimpleMovingAverage(self.market, interval, sma_short)
        self.sma = simple_moving_average.SimpleMovingAverage(self.market, interval, sma_long)
        self.vol_change = volume_change_monitor.VolumeChangeMonitor(self.market, interval)
        self.market.apply_signal(self)
        self.cached_high = None
        self.buy_price = None

    def check_condition(self):
        """will run every time a new candle is pulled"""
        print("SMA CROSSOVER STRATEGY receiving data")

        if (self.sma.value is not None) & (self.fma.value is not None) & (self.vol_change.value is not None):
            print("SMA: " + str(self.sma.value))
            print("FMA: " + str(self.fma.value))
            print("VOL Change: " + str(self.vol_change.value) + "%")
            # if we already have a closing high saved, we need to check whether were still crossed over, and if we need to open a trade
            if self.cached_high is not None:
                print("Checking if current price is greater than cached high")
                if not self.fma.value > self.sma.value: # if we're no longer fma > sma, forget about saved high
                    print("FMA has gone below SMA, forgetting cached high")
                    self.cached_high = None
                    return False
                if self.market.latest_candle['5m'][2] > self.cached_high: # open a trade if the latest high is greater than the cached high
                    print("Current high of " + str(self.market.latest_candle['5m'][2]) + " has exceeded cached high of " + str(self.cached_high) + ", buy signal generated")
                    return True
                else:
                    return False

            # if fma is not already above sma, and has now crossed, and volume is up 5% from last period, send trade signal
            elif self.cached_high is None and\
                    self.fma.value > self.sma.value and\
                    self.vol_change.value > 5:
                print("FMA has crossed SMA, caching current high of " + str(self.market.latest_candle['5m'][2]))
                self.cached_high = self.market.latest_candle['5m'][2]
                return False
            else:
                return False
        else:
            return False
