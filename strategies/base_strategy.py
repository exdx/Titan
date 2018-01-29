from core.markets import market_watcher
from core.markets import market_simulator
from core.markets import market
from core.markets import position
from collections import defaultdict
from threading import Thread
from queue import Queue

strategies = defaultdict(list)


class BaseStrategy:
    """An abstract class that implements the backbone functionality of a strategy

    Stragies inheriting from this class can specify the following things in their __init__ method:
        - order_quantity - Quantity of asset to buy
        - profit_target_percent - Profit target percent to dictate when to liquidate position
        - position_limit - Number of concurrent positions to be open at the same time
        - fixed_stoploss_percent - Percentage of order price to set a fixed stoploss on each opened position
        - trailing_stoploss_percent - Percentage of each candle price to set fixed stoploss (updated each candle)

    All strategies should pass in the following in the constructor:
        - interval - time period for candles (i.e. '5m')
        - exchange - ccxt supported exchange (i.e. 'bittrex' or 'binance')
        - base_currency - currency to trade (i.e. 'ETH')
        - quote_currency - currency quotes are in (i.e. 'BTC')
        - is_simulated - should this be a simulation? True or False
        - simulated_quote_balance - the starting balance of the simulation
    A strategy inheriting from this class is an algorithm running on a specific exchange on a single trading pair
    """
    def __init__(self, interval, exchange, base_currency, quote_currency, is_simulated, simulated_quote_balance=0):
        self.market = None
        self.exchange = exchange
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.__thread = Thread(target=self.__run)
        self.__jobs = Queue()  # create job queue
        self.__running = False
        self.is_simulated = is_simulated
        self.starting_balance = simulated_quote_balance
        self.positions = []
        self.interval = interval
        self.name = None
        self.order_quantity = None
        self.position_limit = None
        self.profit_target_percent = None
        self.fixed_stoploss_percent = None
        self.trailing_stoploss_percent = None
        self.__initialize()
        strategies[interval].append(self)

    def start(self):
        """Subscribe the strategy to the correct market watcher for historical to finish syncing as well as for latest candles"""
        if not self.__running:
            self.__thread.start()

    def stop(self):
        """Stop the strategy"""
        self.__running = False

    def on_data(self, candle):
       """Logic to be implemented by inheriting strategies"""

    def get_open_position_count(self):
        """Get number of long positions opened by this strategy and currently open"""
        count = len([p for p in self.positions if p.is_open])
        print(str(count) + " long positions open")
        return count

    def long(self):
        """Open a long position"""
        if self.is_simulated:
            self.positions.append(market_simulator.open_long_position_simulation(self.market, self.order_quantity,
                                                                                 self.market.latest_candle[self.interval][3],
                                                                                 self.fixed_stoploss_percent,
                                                                                 self.trailing_stoploss_percent,
                                                                                 self.profit_target_percent))
        else:
            self.positions.append(position.open_long_position(self.market, self.order_quantity,
                                                          self.market.get_best_ask(),
                                                          self.fixed_stoploss_percent,
                                                          self.trailing_stoploss_percent,
                                                          self.profit_target_percent))

    def __initialize(self):
        if self.is_simulated:
            self.market = market_simulator.MarketSimulator(self.exchange, self.base_currency, self.quote_currency,
                                                           self.starting_balance)
            self.__jobs.put(lambda: market_watcher.subscribe(self.market.exchange.id, self.market.base_currency,
                                                             self.market.quote_currency, self.interval,
                                                             self.__update))
            market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                                self.market.quote_currency, self.interval, self.__run_simulation)

        else:
            self.market = market.Market(self.exchange, self.base_currency, self.quote_currency)
            self.__jobs.put(lambda: market_watcher.subscribe(self.market.exchange.id, self.market.base_currency,
                                                             self.market.quote_currency, self.interval, self.__update))
            market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                                self.market.quote_currency, self.interval, self.__warmup)

    def __warmup(self, periods=None):
        def warmup(periods):
            """Run TA calculations on historical data"""
            if periods is None:
                historical_data = self.market.get_historical_candles(self.interval)
            else:
                historical_data = self.market.get_historical_candles(self.interval, periods)
            for candle in historical_data:
                self.market.update(self.interval, candle)
        self.__jobs.put(warmup(periods))

    def __update(self, candle):
        def update(candle):
            """Run updates on all markets/indicators/signal generators running in strategy"""
            self.market.update(self.interval, candle)
            self.__update_positions()
            self.on_data(candle)
        self.__jobs.put(lambda: update(candle))

    def __run_simulation(self, candle_set=None):
        def run_simulation(candle_set):
            """Grab historical candles from DB and run strategy on them"""
            print('Simulating strategy for market...')
            if candle_set is None:
                candle_set = self.market.get_historical_candles(self.interval, 1000)
            self.simulating = True
            for entry in candle_set:
                self.__update(entry)
            self.simulating = False
        self.__jobs.put(lambda: run_simulation(candle_set))

    def __update_positions(self):
        """Trigger positions opened by this strategy to check if stop losses or profit targets have been met
        Should be called on every candle"""
        for p in self.positions:
            if p.is_open:
                p.update()

    def __run(self):
        """Start listener queue waiting for ticks"""
        self.__running = True
        while self.__running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                try:
                    job()
                except Exception as e:
                    print(job.__name__ + " threw error:\n" + str(e))

