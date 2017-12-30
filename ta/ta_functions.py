from core.database import ohlcv_functions
from pyti.simple_moving_average import simple_moving_average as sma
from pyti.exponential_moving_average import exponential_moving_average as ema
from core.database import connection_manager
from threading import Lock

engine = connection_manager.engine
conn = engine.connect()
lock = Lock()


class SimpleMovingAverage:
    def __init__(self, market, interval, slow_periods, fast_periods):
        self.interval = interval
        self.market = market
        self.slow_periods = slow_periods
        self.fast_periods = fast_periods
        self.write_strategy_description_to_db()
        self.sma_slow_result = None
        self.sma_fast_result = None
        self.slow_dataset = None
        self.fast_dataset = None
        self.close = None
        self.timestamp = None

    def next_calculation(self):
        """get latest N candles from market, do calculation, write results to db"""
        self.slow_dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.interval, self.slow_periods)
        self.fast_dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.interval, self.fast_periods)
        self.do_calculation()
        self.write_ta_statistic_to_db()

    def calculate_historical(self):
        """do calculations on historical market data if there are enough candles to do the calculation - otherwise return NA"""
        self.slow_dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair,self.market.interval, self.slow_periods)
        if len(self.slow_dataset['Close'].tolist()) < self.slow_periods:
            self.sma_slow_result = 'NA'
            self.sma_fast_result = 'NA'
        else:
            self.do_calculation()

        self.write_ta_statistic_to_db()

    def do_calculation(self):
        self.sma_slow_result = sma(self.slow_dataset['Close'].tolist(), self.slow_periods)[-1]
        self.sma_fast_result = sma(self.fast_dataset['Close'].tolist(), self.fast_periods)[-1]
        self.close = self.slow_dataset['Close'].tolist()[0]
        self.timestamp = self.slow_dataset['Timestamp'].tolist()[0]

    def write_ta_statistic_to_db(self):
        """Inserts average into table, depending on the column whether it is the slow moving average or the fast moving average"""
        with lock:
                ins = connection_manager.TAMovingAverage.insert().values(Pair=self.market.analysis_pair,Time=self.timestamp,Close=self.close,MA_SLOW_INTERVAL=self.slow_periods,MA_SLOW=self.sma_slow_result,MA_FAST_INTERVAL=self.fast_periods,MA_FAST=self.sma_fast_result)
                conn.execute(ins)
                print('Wrote statistic to db...')

    def write_strategy_description_to_db(self):
        '''Add ID and description to TAIdentifier table'''
        with lock:
            ins = connection_manager.TAIdentifier.insert().values(TA_ID=1, Description='A basic SMA Crossover Strategy')
            conn.execute(ins)

    def convert_periods_to_time(self):
        '''Convert 5m period counts to hours or days, to make it more readable'''
        pass

#
# class ExponentialMovingAverage:
#     def __init__(self, interval, periods, market, speed):
#         self.interval = interval
#         self.periods = periods
#         self.market = market
#         self.speed = speed
#         self.write_ta_statistic_to_db()
#
#     def next_calculation(self):
#         """get latest N candles from market, do calculation, write results to db"""
#         self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair, self.interval, self.periods)
#         self.do_calculation()
#         self.write_ta_statistic_to_db()
#
#     def calculate_historical(self):
#         """do calculations on historical market data if there are enough candles to do the calculation - otherwise return NA"""
#         self.dataset = ohlcv_functions.get_latest_N_candles_as_df(self.market.exchange.id, self.market.analysis_pair,self.market.interval, self.periods)
#         if len(self.dataset['Close'].tolist()) < self.periods:
#             self.ema_result = 'NA'
#         else:
#             self.do_calculation()
#
#         self.write_ta_statistic_to_db()
#
#     def do_calculation(self):
#         ema_list = ema(self.dataset['Close'].tolist(), self.periods)
#         self.ema_result = ema_list[-1]
#         return self.ema_result
#
#     def write_ta_statistic_to_db(self):
#         '''Inserts average into table, depending on the column whether it is the slow moving average or the fast moving average'''
#         with lock:
#             if self.speed == 'slow':
#                 ins = connection_manager.TAMovingAverage.insert().values(SMA_SLOW_INTERVAL=self.periods, SMA_SLOW=self.ema_result)
#                 conn.execute(ins)
#                 print('Writing Slow EMA statistic to db...')
#             elif self.speed == 'fast':
#                 ins = connection_manager.TAMovingAverage.insert().values(SMA_FAST_INTERVAL=self.periods,SMA_FAST=self.ema_result)
#                 conn.execute(ins)
#                 print('Writing Fast EMA statistic to db...')
#
#     def write_strategy_description_to_db(self):
#         '''Add ID and description to TAIdentifier table'''
#         with lock:
#             ins = connection_manager.TAIdentifier.insert().values(TA_ID=2, Description='A basic EMA Crossover Strategy')
#             conn.execute(ins)
#
#     def convert_periods_to_time(self):
#         '''Convert 5m period counts to hours or days, to make it more readable'''
#         pass
