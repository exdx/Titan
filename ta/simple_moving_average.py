from core.database import ohlcv_functions
from pyti.simple_moving_average import simple_moving_average as sma
from core.database import database
from ta.base_indicator import BaseIndicator

engine = database.engine
conn = engine.connect()


class SimpleMovingAverage(BaseIndicator):
    def __init__(self, market, interval, periods):
        super().__init__(market, interval, periods)
        self.write_strategy_description_to_db()
        self.close = None
        self.timestamp = None
        self.value = None

    def next_calculation(self, candle):
        """Get latest N candles from market, do calculation, write results to db"""
        self.update_dataset(candle)
        if len(self.dataset) == self.periods:
            self.do_calculation(candle)
            self.write_ta_statistic_to_db(candle)
            print("Calculated new moving average: " + str(self.value))

    def do_calculation(self, candle):
        data = list(c[4] for c in self.dataset)
        self.value = round(sma(data, self.periods)[-1], 6)
        self.close = candle[4]
        self.timestamp = ohlcv_functions.convert_timestamp_to_date(candle[0])

    def write_ta_statistic_to_db(self, candle):
        """Inserts average into table"""
        with database.lock:
                ins = database.TAMovingAverage.insert().values(Exchange=self.market.exchange.id, Pair=self.market.analysis_pair, Time=self.timestamp, Close=self.close, Interval=self.periods, MovingAverage=self.value, TimestampRaw=candle[0])
                conn.execute(ins)
                print('Wrote statistic to db...')

    def write_strategy_description_to_db(self):
        """Add ID and description to TAIdentifier table"""
        with database.lock:
            ins = database.TAIdentifier.insert().values(Description='A basic SMA Crossover Strategy - Moving Average {}'.format(self.periods))
            conn.execute(ins)
