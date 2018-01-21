from core.markets import ticker
from core.markets import market_simulator
from core.markets import position_manager
from collections import defaultdict

strategies = defaultdict(list)


def update_all_strategies(interval):
    for strategy in strategies[interval]:
        strategy.update()


class BaseStrategy:

    def __init__(self, interval):
        self.interval = interval
        self.position = None
        self.order_quantity = None
        self.position_limit = None
        self.market = None
        self.buy_signal = None
        self.profit_target_percent = None
        self.fixed_stoploss_percent = None
        self.trailing_stoploss_percent = None
        strategies[interval].append(self)

    def update(self):
        if self.position is not None:
            if self.position.is_open:
                self.position.update()
            elif self.buy_signal.check_condition():
                self.long()
        elif self.buy_signal.check_condition():
            self.long()

    def long(self):
        self.position = position_manager.open_long_position(self.market, self.order_quantity,
                                                            self.market.get_best_ask(),
                                                            self.fixed_stoploss_percent,
                                                            self.trailing_stoploss_percent,
                                                            self.profit_target_percent)


class StrategySimulator(BaseStrategy):

    def long(self):
        self.position = market_simulator.open_long_position_simulation(self.market, self.order_quantity,
                                                                       self.market.latest_candle[self.interval][3],
                                                                       self.fixed_stoploss_percent,
                                                                       self.trailing_stoploss_percent,
                                                                       self.profit_target_percent)