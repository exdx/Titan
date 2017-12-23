from core.database import ohlcv_functions
from core.listener import market_listener
from pyti.simple_moving_average import simple_moving_average as sma
from core.database import connection_manager

engine = connection_manager.engine
conn = engine.connect()

class SimpleMovingAverage:
    def __init__(self, periods):
        self.periods = periods

    def ta_get_dataset(self):
        if market_listener.Listener.historical_loaded:
            self.dataset = ohlcv_functions.get_latest_N_candles_as_df(market_listener.Listener.exchange, market_listener.Listener.analysis_pair, market_listener.Listener.interval, self.periods)
        else:
            print("Historical Data not yet loaded...")
            pass

    def do_calculation(self):
        self.sma_result = sma(self.dataset['Close'].tolist(), self.periods)

    def write_ta_statistic_to_db(self):
        '''Inserts average into table'''
        ins = connection_manager.TA_Det_x1.insert().values(SMA_SLOW_INTERVAL=self.periods, SMA_SLOW=self.sma_result)
        conn.execute(ins)
        print('Writing SMA statistic to db...')

    def convert_interval_to_time(self):
        pass


