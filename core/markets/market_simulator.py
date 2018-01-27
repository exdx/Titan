from core.markets.market import Market
from core.database import ohlcv_functions
from core.markets import position
from core.markets import order
from strategies import base_strategy

long_positions = 0


class MarketSimulator(Market):
    """Wrapper for market that allows simulating simple buys and sells"""
    def __init__(self, exchange, base_currency, quote_currency, quote_currency_balance):
        super().__init__(exchange, base_currency, quote_currency)
        self.starting_balance = quote_currency_balance
        self.quote_balance = quote_currency_balance
        self.base_balance = 0
        self.simulating = False

    def limit_buy(self, quantity, price):
        if self.quote_balance >= quantity * price:
            self.quote_balance = self.quote_balance - quantity * price
            self.base_balance = self.base_balance + quantity
            order.write_order_to_db(self.exchange.id, self.analysis_pair, "buy", quantity, price, "simulated")
            print()
            print("Executed buy simulation of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            print(self.quote_currency + " balance: " + str(self.quote_balance))
            print(self.base_currency + " balance: " + str(self.base_balance))
            print()
        else:
            print("Insufficient balance for simulation buy")

    def limit_sell(self, quantity, price):
        if self.base_balance >= quantity:
            self.base_balance = self.base_balance - quantity
            self.quote_balance = self.quote_balance + quantity * price
            order.write_order_to_db(self.exchange.id, self.analysis_pair, "sell", quantity, price, "simulated")
            print()
            print("Executed sell simulation of " + str(quantity) + " " + self.base_currency + " for " + str(price) + " " + self.quote_currency)
            print(self.quote_currency + " balance: " + str(self.quote_balance))
            print(self.base_currency + " balance: " + str(self.base_balance))
            print()
        else:
            print("Insufficient balance for simulation sell")

    def market_buy(self, quantity):
        if self.quote_balance >= quantity * self.get_ask_price():
            self.quote_balance = self.quote_balance - quantity * self.get_ask_price()
            self.base_balance = self.base_balance + quantity
            print()
            print("Executed buy simulation of " + str(quantity) + " " + self.base_currency + " for " + str(self.get_ask_price()) + " " + self.quote_currency)
            print(self.quote_currency + " balance: " + str(self.quote_balance))
            print(self.base_currency + " balance: " + str(self.base_balance))
            print()
        else:
            print("Insufficient balance for simulation buy")

    def market_sell(self, quantity):
        if self.base_balance >= quantity:
            self.base_balance = self.base_balance - quantity
            self.quote_balance = self.quote_balance + quantity * self.get_bid_price()
            print()
            print("Executed sell simulation of " + str(quantity) + " " + self.base_currency + " for " + str(self.get_bid_price()) + " " + self.quote_currency)
            print(self.quote_currency + " balance: " + str(self.quote_balance))
            print(self.base_currency + " balance: " + str(self.base_balance))
            print()
        else:
            print("Insufficient balance for simulation sell")

    def get_ask_price(self):
        """Get ask price for simulation"""
        if not self.simulating:
            """if operating on live data, use actual ask"""
            return self.exchange.fetchTicker(self.analysis_pair)['ask']
        else:
            """if operating on historical data, use close"""
            return self.latest_candle['5m'][4]

    def get_bid_price(self):
        if not self.simulating:
            """if operating on live data, use actual ask"""
            return self.exchange.fetchTicker(self.analysis_pair)['bid']
        else:
            """if operating on historical data, use close"""
            return self.latest_candle['5m'][4]

    def simulate_on_historical(self, interval, strategy):
        """Load all historical candles to database"""
        print('Simulating candles for market...')
        data = self.get_all_historical_candles(interval)
        self.simulating = True
        for entry in data:
            self.latest_candle[interval] = entry
            strategy._update(entry)
        print('Simulation on historical data done')
        self.simulating = False

    def get_wallet_balance(self):
        return self.quote_balance


def open_long_position_simulation(market, amount, price, fixed_stoploss, trailing_stoploss_percent, profit_target_percent):
    """Create simulated long position"""
    print("Opening simulated long position")
    position = LongPositionSimulator(market, amount, price, fixed_stoploss, trailing_stoploss_percent, profit_target_percent)
    position.open()
    return position


def open_short_position_simulation(market, amount, price):
    """Create simulated short position"""
    print("Opening simulated short position")
    position = ShortPositionSimulator(market, amount, price)
    position.open()
    return position


class LongPositionSimulator(position.LongPosition):
    """Simulated long position. Overrides the functionality of creating an actual order to use the MarketSimulators balance and calculations"""
    def __init__(self, market, amount, price, fixed_stoploss, trailing_stoploss_percent, profit_target_percent):
        super().__init__(market, amount, price, fixed_stoploss, trailing_stoploss_percent, profit_target_percent)

    def liquidate_position(self):
        """Will use this method to actually create the order that liquidates the position"""
        print("Closing simulated long position")
        open_short_position_simulation(self.market, self.amount, self.market.latest_candle['5m'][3])
        self.is_open = False

    def open(self):
        self.market.limit_buy(self.amount, self.price)
        self.is_open = True

    def update(self):
        """Use this method to trigger position to check if profit target has been met, and re-set trailiing stop loss"""
        print("UPDATING LONG POSITION")
        if self.market.latest_candle['5m'][3] < self.trailing_stoploss or\
            self.market.latest_candle['5m'][3] < self.fixed_stoploss or\
            self.market.latest_candle['5m'][3] >= self.profit_target:  # check price against last calculated trailing stoploss
                self.liquidate_position()
        # re-calculate trailing stoploss
        self.trailing_stoploss = self.calculate_trailing_stoploss()


class ShortPositionSimulator(position.ShortPosition):
    """Simulated short position. Overrides the functionality of creating an actual order to use the MarketSimulators balance and calculations"""
    def __init__(self, market, amount, price):
        super().__init__(market, amount, price)

    def open(self):
        self.market.limit_sell(self.amount, self.price)