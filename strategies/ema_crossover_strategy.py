import core.database
import core.listener
from ta import simple_moving_average
from ta import volume_change_monitor
from core.markets import market
from core.markets import position_manager


class CrossoverStrategy:

    def __init__(self):
        """here is where you determine your starting capital, markets to use, etc"""
        self.starting_capital = 1000
        self.market = market.Market('bittrex', 'ETH', 'BTC')
        self.fma = simple_moving_average.SimpleMovingAverage(self.market, "5m", 12)
        self.sma = simple_moving_average.SimpleMovingAverage(self.market, "5m", 1440)
        self.vol_change = volume_change_monitor.VolumeChangeMonitor(self.market, "5m")
        self.crossed = lambda: self.fma > self.sma
        self.open_position = False

    def on_data(self):
        """will run every time a new candle is pulled"""
        if not self.crossed() &\
               self.fma.value > self.sma.value &\
               self.vol_change.value > .05:
            position_manager.open_position(market, amount, price)
