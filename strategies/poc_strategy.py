from strategies.base_strategy import BaseStrategy
from signal_generators import sma_crossover_signal


class PocStrategy(BaseStrategy):
    """A strategy using the SMA crossover signal generator as a buy signal
    This strategy will trigger the SMA crossover signal on every candle and check for buy conditions
    If the condition returns true, the strategy will open a long position it does not have up to (position_limit) opened
    Each position opened will automatically sell itself off when its price (profit_target_percent*buy price) is met
    """
    def __init__(self, interval, exchange, base_currency, quote_currency, fma_periods, sma_periods, is_simulated, sim_balance=0):
        super().__init__(interval, exchange, base_currency, quote_currency, is_simulated, sim_balance)
        self.order_quantity = 1
        self.position_limit = 1
        self.buy_signal = sma_crossover_signal.SmaCrossoverSignal(self.market, self.interval, fma_periods, sma_periods)
        self.profit_target_percent = 1.03
        self.fixed_stoploss_percent = .90
        self.trailing_stoploss_percent = .97

    def on_data(self, candle):
        buy_condition = self.buy_signal.check_condition(candle)
        if self.get_open_position_count() >= self.position_limit:
            pass
        elif buy_condition:
            self.long()
