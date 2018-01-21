from core.markets import market_simulator
from core.markets import ticker
from strategies.base_strategy import BaseStrategy
from strategies.base_strategy import StrategySimulator
from signal_generators import sma_crossover_signal


class PocStrategy(StrategySimulator):

    def start(self):
        self.order_quantity = 1
        self.position_limit = 1
        self.market = market_simulator.MarketSimulator('bittrex', 'ETH', 'BTC', 10)
        self.buy_signal = sma_crossover_signal.SmaCrossoverSignal(self.market, 100, 770, self.interval)
        self.profit_target_percent = 1.03
        self.fixed_stoploss_percent = .90
        self.trailing_stoploss_percent = .97
        self.market.load_historical(self.interval)

