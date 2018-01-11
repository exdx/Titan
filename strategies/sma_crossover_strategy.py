import core.database
from ta import simple_moving_average
from ta import volume_change_monitor
from strategies.base_strategy import BaseStrategy
from core.markets import position_manager

#an implementation of the simple crossover strategy defined in the google doc
class SmaCrossoverStrategy(BaseStrategy):
    def __init__(self, market, sma_short, sma_long):
        """here is where you determine your values to keep track of, etc"""
        super().__init__()
        self.market = market
        self.fma = simple_moving_average.SimpleMovingAverage(self.market, "5m", sma_short)
        self.sma = simple_moving_average.SimpleMovingAverage(self.market, "5m", sma_long)
        self.vol_change = volume_change_monitor.VolumeChangeMonitor(self.market, "5m")
        self.market.apply_strategy(self)
        self.cached_high = None
        self.open_position = False
        self.buy_price = None

    def on_data(self):
        """will run every time a new candle is pulled"""
        print("SMA CROSSOVER STRATEGY receiving data")
        if self.open_position:
            print("Position currently open, checking if should sell")
            if (self.market.get_bid_price() / self.buy_price) > .03:
                self.market.sell(1)
                self.open_position = False
                print("Closed position")

        elif (self.sma.value is not None) & (self.fma.value is not None) & (self.vol_change.value is not None):
            print("SMA: " + self.sma.value)
            print("FMA: " + self.fma.value)
            print("VOL Change: " + self.vol_change.value)
            # if we already have a closing high saved, we need to check whether were still crossed over, and if we need to open a trade
            if self.cached_high is not None:
                print("Checking if current price is greater than cached high")
                if not self.fma.value > self.sma.value: # if we're no longer fma > sma, forget about saved high
                    print("FMA has gone below SMA, forgetting cached high")
                    self.cached_high = None
                    return
                if self.market.latest_candle[2] > self.cached_high: # open a trade if the latest high is greater than the cached high
                    print("Price has exceeded cached high, opening position")

                    # here is where the action goes down
                    self.market.buy(1)
                    self.buy_price = self.market.get_ask_price()
                    self.open_position = True
                    return
                    # here we can send a buy signal to our trade executor or some other entity
                    # need to decide what we want to decide here and what we want the other entity to decide (amount etc)

                    #also if we want this strategy to continually run, we can keep a list of positions and continually open them as conditions work out

            # if fma is not already above sma, and has now crossed, and volume is up 5% from last period, send trade signal
            if not self.fma.value > self.sma.value and\
                   self.fma.value > self.sma.value and\
                   self.vol_change.value > .05:
                print("FMA has crossed SMA, caching current high")
                self.cached_high = self.market.latest_candle[2]
