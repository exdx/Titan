from core.markets import ticker
from core.markets import market_simulator
from core.markets import market
from core.markets import position
from collections import defaultdict

strategies = defaultdict(list)


def update_all_strategies(interval):
    for strategy in strategies[interval]:
        strategy.update()


class BaseStrategy:

    def __init__(self, interval, exchange, base_currency, quote_currency, is_simulated):
        self.market = None
        if is_simulated:
            self.market = market_simulator.MarketSimulator(exchange, base_currency, quote_currency, 10)
        else:
            self.market = market.Market(exchange, base_currency, quote_currency)
        self.interval = interval
        self.order_quantity = None
        self.position_limit = None
        self.buy_signal = None
        self.profit_target_percent = None
        self.fixed_stoploss_percent = None
        self.trailing_stoploss_percent = None
        self.positions = []
        strategies[interval].append(self)

    def start(self):
        self.market.load_historical(self.interval)

    def start_simulation(self):


    def update(self):
        self.update_positions()
        buy_condition = self.buy_signal.check_condition()
        if self.get_open_position_count() >= self.position_limit:
            pass
        elif buy_condition:
            self.long()

    def get_open_position_count(self):
        count = len([p for p in self.positions if p.is_open])
        print(str(count) + " long positions open")
        return count

    def update_positions(self):
        for p in self.positions:
            if p.is_open:
                p.update()

    def long(self):
        self.positions.append(position.open_long_position(self.market, self.order_quantity,
                                                          self.market.get_best_ask(),
                                                          self.fixed_stoploss_percent,
                                                          self.trailing_stoploss_percent,
                                                          self.profit_target_percent))


class StrategySimulator(BaseStrategy):

    def long(self):
        self.positions.append(market_simulator.open_long_position_simulation(self.market, self.order_quantity,
                                                                       self.market.latest_candle[self.interval][3],
                                                                       self.fixed_stoploss_percent,
                                                                       self.trailing_stoploss_percent,
                                                                       self.profit_target_percent))