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
    """An abstract class that implements the backbone functionality of a strategy

     Stragies inheriting from this class can specify the following things in their __init__ method:
         - buy_signal - Signal generator to initiate the opening of a long position
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
        self.__thread = Thread(target=self.__run)
        self.__jobs = Queue()  # create job queue
        self.running = False
        self.positions = []
        self.interval = interval
        self.is_simulated = is_simulated
        self.name = None
        if self.is_simulated:
            self.market = market_simulator.MarketSimulator(exchange, base_currency, quote_currency, simulated_quote_balance, self)
        else:
            self.market = market.Market(exchange, base_currency, quote_currency, self)
        strategies.append(self)
        self.strategy_id = len(strategies)
        self.ui_messages = Queue()

    def start(self):
        """Start thread and subscribe to candle updates"""
        self.__jobs.put(lambda: market_watcher.subscribe(self.market.exchange.id, self.market.base_currency, self.market.quote_currency, self.interval, self.__update))
        self.__thread.start()

    def warmup(self):
        """Queue warmup when market data has been synced"""
        market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                            self.market.quote_currency, self.interval, self.__warmup)

    def run_simulation(self):
        """Queue simulation when market data has been synced"""
        if self.is_simulated:
            market_watcher.subscribe_historical(self.market.exchange.id, self.market.base_currency,
                                            self.market.quote_currency, self.interval, self.__run_simulation)

    def __warmup(self, periods=None):
        """Update TA indicators on specified number of historical periods"""
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
        """Start a simulation on historical candles (runs update method on historical candles)"""
        def run_simulation(candle_set):
            self.print_message("Simulating strategy for market " + self.market.exchange.id + " " + self.market.analysis_pair)
            if candle_set is None:
                candle_set = self.market.get_historical_candles(self.interval, 1000)
            self.simulating = True
            for entry in candle_set:
                self.__update(candle=entry)
            self.simulating = False
        self.__jobs.put(lambda: run_simulation(candle_set))

    def __update(self, candle):
        """Run updates on all markets/indicators/signal generators running in strategy"""
        def update(candle):
            print("Updating strategy")
            self.print_message("Received new candle")
            self.market.update(self.interval, candle)
            self.__update_positions()
            self.on_data(candle)
            self.print_message("Simulation BTC balance: " + str(self.market.get_wallet_balance()))
        self.__jobs.put(lambda: update(candle))

    def on_data(self, candle):
        """Will be called on each candle, this method is to be overriden by inheriting classes"""
        pass

    def get_open_position_count(self):
        """Check how many positions this strategy has open"""
        count = len([p for p in self.positions if p.is_open])
        self.print_message(str(count) + " long positions open")
        return count

    def __update_positions(self):
        """Loop through all positions opened by the strategy"""
        for p in self.positions:
            if p.is_open:
                p.update()

    def long(self, order_quantity, fixed_stoploss_percent, trailing_stoploss_percent, profit_target_percent):
        """Open long position"""
        if self.is_simulated:
            """Open simulated long position"""
            self.print_message("Going long on " + self.market.analysis_pair)
            self.positions.append(market_simulator.open_long_position_simulation(self.market, order_quantity,
                                                                                 self.market.latest_candle[
                                                                                     self.interval][3],
                                                                                 fixed_stoploss_percent,
                                                                                 trailing_stoploss_percent,
                                                                                 profit_target_percent))
        else:
            """LIVE long position"""
            self.print_message("Going long on " + self.market.analysis_pair)
            self.positions.append(position.open_long_position(self.market, order_quantity,
                                                          self.market.get_best_ask(),
                                                          fixed_stoploss_percent,
                                                          trailing_stoploss_percent,
                                                          profit_target_percent))

    def __run(self):
        """Start the strategy thread waiting for commands"""
        self.print_message("Starting strategy " + str(self.strategy_id))
        self.running = True
        while self.running:
            if not self.__jobs.empty():
                job = self.__jobs.get()
                try:
                    job()
                except Exception as e:
                    print(e)
                    logger.error(job.__name__ + " threw error:\n" + str(e))


    def print_message(self, msg):
        """Add to a queue of messages that can be consumed by the UI"""
        print(str("Strategy " + str(self.strategy_id) + ": " + msg))
        logger.info(msg)
        self.ui_messages.put(msg)


