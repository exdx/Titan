from core.database import ohlcv_functions
from core.markets import exchange
from pyti.simple_moving_average import simple_moving_average as sma
from core.database import connection_manager
from threading import Lock

engine = connection_manager.engine
conn = engine.connect()
lock = Lock()

class SimpleMovingAverage:
    def __init__(self, periods, market):
        self.periods = periods
        self.market = market

    def next_calculation(self):
        """get latest N candles from market, do calculation, write results to db"""
        latest = self.market.latest_candle

        self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.market.interval, self.periods)
        self.do_calculation()
        self.write_ta_statistic_to_db()



    def calculate_historical(self):
        """do calculations on historical market data if there are enough candles to do the calculation - otherwise return NA"""
        self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair,self.market.interval, self.periods)
        if len(self.dataset['Close'].tolist()) < self.periods:
            self.sma_result = 'NA'
        else:
            self.do_calculation()

        self.write_ta_statistic_to_db()



    def do_calculation(self):
        self.sma_result = sma(self.dataset['Close'].tolist(), self.periods)
        return self.sma_result


    def write_ta_statistic_to_db(self):
        '''Inserts average into table'''
        with Lock():
            ins = connection_manager.TA_Det_x1.insert().values(SMA_SLOW_INTERVAL=self.periods, SMA_SLOW=self.sma_result)
            conn.execute(ins)
            print('Writing SMA statistic to db...')