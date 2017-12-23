import time
import ccxt
from core.database import ohlcv_functions
from threading import Thread
from queue import Queue

listeners = [] # static list of listeners - listeners are added as they are instantiated

class Listener:
    """Represents a listener for a given market. This is implemented as an active object or "actor" with multiple thread support.
    When started, the listener will wait to be ticked, where it will pull the latest candle data and add it to the database"""
    def __init__(self, exchange, base_currency, quote_currency, interval):
        self._thread = Thread(target=self.run)  # create thread for listener
        self._jobs = Queue()  # create job queue
        self._running = True
        self._thread.start()
        self.exchange = exchange
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.interval = interval
        self.analysis_pair = '{}/{}'.format(self.base_currency, self.quote_currency)
        self.analysis_market = self.exchange.load_markets()[self.analysis_pair]
        self.wait_period = get_wait_period_from_interval(self.interval)
        self.historical_loaded = False  # mark historical data unloaded
        listeners.append(self)  # add to static list of listeners


    def run(self):
        """Start listener queue waiting for ticks"""
        while self._running:
            if not self._jobs.empty():
                job = self._jobs.get()
                try:
                    job()
                except Exception as e:
                    print(e)
                    #print('Tick error')


    def stop(self):
        """Stop listener queue"""
        self._running = False

    def tick(self):
        """Initiate a pull of the latest candle, making sure not to pull a duplicate candle"""
        def do_tick():
            data = try_get_data(self.exchange, self.analysis_pair, self.interval)
            while ohlcv_functions.has_candle(data[-1], self.exchange.id, self.analysis_pair, self.interval):
                print('Candle already contained in DB, retrying...')
                time.sleep(self.exchange.rateLimit / 1000)
                data = try_get_data(self.exchange, self.analysis_pair, self.interval)
            self.add_candle(data[-1])
        if self.historical_loaded:  # only add new candles if historical data has been loaded
            self._jobs.put(do_tick)

    def add_historical_candles(self):
        """Load all historical candles to database"""
        def do_add():
            print('Getting historical candles for market...')

            data = self.exchange.fetch_ohlcv(self.analysis_pair, self.interval)
            for entry in data:
               self.add_candle(entry)
               print('Writing candle ' + str(entry[0]) + ' to database')
            self.historical_loaded = True
        self._jobs.put(do_add)

    def add_candle(self, candle_data):
        """Add a candle to the database"""
        ohlcv_functions.insert_data_into_ohlcv_table(self.exchange.id,self.analysis_pair,self.interval,candle_data)



def try_get_data(exchange, analysis_pair, interval):
    """method to pull data from the API of the exchange passed in"""
    try:
        return exchange.fetch_ohlcv(analysis_pair, interval)
    except:
        print("Error getting latest " + interval + " candle for " + analysis_pair + " on " + exchange.id)

def load_historical():
    """Pull in historical data on all instantiated listeners (as is, this must be called before any ticks take place)"""
    for listener in listeners:
        listener.add_historical_candles()

def tick_all():
    """Loop through all the instantiated listeners and initiated a tick"""
    for listener in listeners:
        listener.tick()

def get_wait_period_from_interval(interval):
    """Convert given interval to integer wait period (will be more helpful when we support different intervals)"""
    if interval == "1m":
        return 55
    elif interval == "5m":
        return 300
