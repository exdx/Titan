from core.markets.market import Market
from core.database import ohlcv_functions

class MarketSimulator(Market):
    """Wrapper for market that allows simulating simple buys and sells and market price"""
    def __init__(self, exchange, base_currency, quote_currency, quote_currency_balance):
        super().__init__(exchange, base_currency, quote_currency)
        self.starting_balance = quote_currency_balance
        self.quote_balance = quote_currency_balance
        self.base_balance = 0


    def buy(self, quantity):
        if self.quote_balance >= quantity * self.get_ask_price():
            self.quote_balance = self.quote_balance - quantity * self.get_ask_price()
            self.base_balance = self.base_balance + quantity
            print("Executed buy simulation")
            print(self.quote_currency + " balance: " + self.quote_balance)
            print(self.base_currency + " balance: " + self.base_balance)
        else:
            print("Insufficient balance for simulation buy")

    def sell(self, quantity):
        if self.base_balance >= quantity:
            self.base_balance = self.base_balance - quantity
            self.quote_balance = self.quote_balance + quantity * self.get_bid_price()
            print(self.quote_currency + " balance: " + self.quote_balance)
            print(self.base_currency + " balance: " + self.base_balance)
        else:
            print("Insufficient balance for simulation sell")

    def get_ask_price(self):
        return self.exchange.fetchTicker(self.analysis_pair)['ask']

    def get_bid_price(self):
        return self.exchange.fetchTicker(self.analysis_pair)['bid']

    def _load_historical(self):
        """Load all historical candles to database"""
        print('Getting historical candles for market...')
        data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
        for entry in data:
            ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id, self.analysis_pair, self.interval, entry)
            self.latest_candle = entry
            self._do_ta_calculations()
            self._tick_strategies()
            print('Writing candle ' + str(entry[0]) + ' to database')
        self.historical_loaded = True
        print('Historical data has been loaded.')
