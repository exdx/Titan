from strategies.base_strategy import BaseStrategy
from strategies.base_strategy import StrategySimulator
from signal_generators import sma_crossover_signal


class PocStrategy(StrategySimulator):

    def __init__(self, interval, exchange, base_currency, quote_currency, is_simulated, fma_periods, sma_periods, sim_balance=0):
        super().__init__(interval, exchange, base_currency, quote_currency, is_simulated, sim_balance)
        self.order_quantity = 1
        self.position_limit = 1
        self.buy_signal = sma_crossover_signal.SmaCrossoverSignal(self.market, fma_periods, sma_periods, self.interval)
        self.profit_target_percent = 1.03
        self.fixed_stoploss_percent = .90
        self.trailing_stoploss_percent = .97

