from core.database import ohlcv_functions
from pyti.simple_moving_average import simple_moving_average as sma
from pyti.exponential_moving_average import exponential_moving_average as ema
from core.database import connection_manager
from threading import Lock

engine = connection_manager.engine
conn = engine.connect()
lock = Lock()


class VolumeChangeMonitor:
    def __init__(self, market, interval):
        self.interval = interval
        self.market = market
        self.write_strategy_description_to_db()
        self.__previous_volume = 0
        self.dataset = None
        self.close = None
        self.timestamp = None
        self.value = None

    def next_calculation(self):
        """get latest N candles from market, do calculation, write results to db"""
        self.do_calculation()
        self.write_ta_statistic_to_db()

    def calculate_historical(self):
        """do calculations on historical market data if there are enough candles to do the calculation - otherwise return NA"""


    def do_calculation(self):
        new_volume = self.market.latest_candle[5]
        self.value = (new_volume - self.__previous_volume)/self.__previous_volume
        self.__previous_volume = new_volume
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
            ins = connection_manager.TAIdentifier.insert().values(TA_ID=1, Description='Keeps track of volume changes between each period')
            conn.execute(ins)
