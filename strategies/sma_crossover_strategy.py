import core.database
from core.markets import market_simulator
from ta import simple_moving_average
from ta import volume_change_monitor
from strategies.base_strategy import BaseStrategy
from core.markets import position_manager

#an implementation of the simple crossover strategy defined in the google doc
class SmaCrossoverStrategy(BaseStrategy):
    def __init__(self, sma_short, sma_long):
        """here is where you determine your values to keep track of, etc"""
        super().__init__()
        self.market = market_simulator.MarketSimulator('bittrex', 'ETH', 'BTC', 10)
        self.market.load_historical("5m")
        self.fma = simple_moving_average.SimpleMovingAverage(self.market, "5m", sma_short)
        self.sma = simple_moving_average.SimpleMovingAverage(self.market, "5m", sma_long)
        self.vol_change = volume_change_monitor.VolumeChangeMonitor(self.market, "5m")
        self.market.apply_strategy(self)
        self.cached_high = None
        self.buy_price = None

    def on_data(self):
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
                    return
                if self.market.latest_candle['5m'][2] > self.cached_high: # open a trade if the latest high is greater than the cached high
                    print("Current high of " + str(self.market.latest_candle['5m'][2]) + " has exceeded cached high of " + str(self.cached_high) + ", opening position")
                    market_simulator.open_long_position()
                    return

            # if fma is not already above sma, and has now crossed, and volume is up 5% from last period, send trade signal
            elif self.cached_high is None and\
                    self.fma.value > self.sma.value and\
                    self.vol_change.value > 5:
                print("FMA has crossed SMA, caching current high of " + str(self.market.latest_candle['5m'][2]))
                self.cached_high = self.market.latest_candle['5m'][2]
