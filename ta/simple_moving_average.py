from core.database import ohlcv_functions
from pyti.simple_moving_average import simple_moving_average as sma
from pyti.exponential_moving_average import exponential_moving_average as ema
from core.database import connection_manager
from threading import Lock

engine = connection_manager.engine
conn = engine.connect()
lock = Lock()


class SimpleMovingAverage:
    def __init__(self, market, interval, periods):
        market.apply_indicator(self)
        self.interval = interval
        self.market = market
        self.periods = periods
        self.write_strategy_description_to_db()
        self.dataset = None
        self.close = None
        self.timestamp = None
        self.value = None

    def next_calculation(self):
        """get latest N candles from market, do calculation, write results to db"""
        self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.periods)
        self.do_calculation()
        self.write_ta_statistic_to_db()

    def calculate_historical(self):
        """do calculations on historical market data if there are enough candles to do the calculation - otherwise return NA"""

        #will need more logic to segment and remove remainder candles for doing actual historical calculations

        self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.interval, self.periods)
        if len(self.dataset['Close'].tolist()) < self.periods:
            self.value = 'NA'
        else:
            self.do_calculation()

        self.write_ta_statistic_to_db()

    def do_calculation(self):
        self.value = sma(self.dataset['Close'].tolist(), self.periods)[-1]
        self.close = self.dataset['Close'].tolist()[0]
        self.timestamp = self.dataset['Timestamp'].tolist()[0]

    def write_ta_statistic_to_db(self):
        """Inserts average into table"""
        with lock:
                ins = connection_manager.TAMovingAverage.insert().values(Pair=self.market.analysis_pair, Time=self.timestamp, Close=self.close, INTERVAL=self.periods, VALUE=self.value)
                conn.execute(ins)
                print('Wrote statistic to db...')

    def write_strategy_description_to_db(self):
        '''Add ID and description to TAIdentifier table'''
        with lock:
            ins = connection_manager.TAIdentifier.insert().values(TA_ID=1, Description='A basic SMA Crossover Strategy')
            conn.execute(ins)



