from core.markets import market_watcher
from core.markets import market_simulator
from core.markets import market
from core.markets import position
from threading import Thread
from queue import Queue
import logging

strategies = []
logger = logging.getLogger(__name__)

class BaseStrategy:

    def __init__(self, interval, exchange, base_currency, quote_currency, is_simulated, simulated_quote_balance=0):
        self.market = None
        self.__thread = Thread(target=self.__run)
        self.__jobs = Queue()  # create job queue
        self.running = False
        self.positions = []
        self.interval = interval
        self.is_simulated = is_simulated
        self.name = None
        self.order_quantity = None
        self.position_limit = None
        self.buy_signal = None
        self.profit_target_percent = None
        self.fixed_stoploss_percent = None
        self.trailing_stoploss_percent = None
        if self.is_simulated:
            self.market = market_simulator.MarketSimulator(exchange, base_currency, quote_currency, simulated_quote_balance, self)
        else:
            self.market = market.Market(exchange, base_currency, quote_currency, self)
        strategies.append(self)
        self.strategy_id = len(strategies)
        self.ui_messages = Queue()

    def start(self):
        self.__jobs.put(lambda: market_watcher.subscribe(self.market.exchange.id, self.market.base_currency, self.market.quote_currency, self.interval, self.__update))
        self.__thread.start()

    def warmup(self):
        market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                            self.market.quote_currency, self.interval, self.__warmup)

    def run_simulation(self):
        if self.is_simulated:
            market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                            self.market.quote_currency, self.interval, self.__run_simulation)

    def __warmup(self, periods=None):
        def warmup(periods):
            self.print_message("Warming up strategy")
            if periods is None:
                historical_data = self.market.get_historical_candles(self.interval)
            else:
                historical_data = self.market.get_historical_candles(self.interval, periods)
            for candle in historical_data:
                self.market.update(self.interval, candle)
        self.__jobs.put(warmup(periods))

    def __run_simulation(self, candle_set=None):
        """Load all historical candles to database"""
        def run_simulation(candle_set):
            self.print_message("Simulating strategy for market " + self.market.exchange.id + " " + self.market.analysis_pair)
            if candle_set is None:
                candle_set = self.market.get_historical_candles(self.interval, 1000)
            self.simulating = True
            for entry in candle_set:
                self.__update(entry)
            self.simulating = False
        self.__jobs.put(lambda: run_simulation(candle_set))

    def __update(self, candle):
        """Run updates on all markets/indicators/signal generators running in strategy"""
        def update(candle):
            self.print_message("Received new candle")
            self.market.update(self.interval, candle)
            self.__update_positions()
            buy_condition = self.buy_signal.check_condition(candle)
            if self.get_open_position_count() >= self.position_limit:
                pass
            elif buy_condition:
                self.long()
            self.print_message("Simulation portfolio value: " + str(self.market.get_wallet_balance()))
        self.__jobs.put(lambda: update(candle))

    def get_open_position_count(self):
        count = len([p for p in self.positions if p.is_open])
        self.print_message(str(count) + " long positions open")
        return count

    def __update_positions(self):
        for p in self.positions:
            if p.is_open:
                p.update()

    def long(self):
        self.print_message("Going long on " + self.market.analysis_pair)
        self.positions.append(position.open_long_position(self.market, self.order_quantity,
                                                          self.market.get_best_ask(),
                                                          self.fixed_stoploss_percent,
                                                          self.trailing_stoploss_percent,
                                                          self.profit_target_percent))

    def __run(self):
        """Start listener queue waiting for ticks"""
        self.print_message("Starting strategy " + str(self.strategy_id))
        self.running = True
        while self.running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                job()
                #try:
                #    job()
                #except Exception as e:
                #    logger.error(job.__name__ + " threw error:\n" + str(e))

    def print_message(self, msg):
        print(str("Strategy " + str(self.strategy_id) + ": " + msg))
        logger.info(msg)
        self.ui_messages.put(msg)


class StrategySimulator(BaseStrategy):

    def long(self):
        self.print_message("Going long on " + self.market.analysis_pair)
        self.positions.append(market_simulator.open_long_position_simulation(self.market, self.order_quantity,
                                                                       self.market.latest_candle[self.interval][3],
                                                                       self.fixed_stoploss_percent,
                                                                       self.trailing_stoploss_percent,
                                                                       self.profit_target_percent))