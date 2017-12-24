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
        """get latest candle from market, do calculation, write results to db"""
        latest = self.market.latest_candle


    def calculate_historical(self):
        """do calculations on historical market data"""



    def ta_get_dataset(self):
        if self.market.historical_loaded:
            self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, exchange.Market.analysis_pair, exchange.Market.interval, self.periods)
        else:
            print("Historical Data not yet loaded...")
            pass

    def do_calculation(self):
        self.sma_result = sma(self.dataset['Close'].tolist(), self.periods)


def write_ta_statistic_to_db(self):
    '''Inserts average into table'''
    with Lock():
        ins = connection_manager.TA_Det_x1.insert().values(SMA_SLOW_INTERVAL=self.periods, SMA_SLOW=self.sma_result)
        conn.execute(ins)
        print('Writing SMA statistic to db...')