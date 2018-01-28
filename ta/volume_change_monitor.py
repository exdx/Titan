from core.database import ohlcv_functions
from core.database import database
from ta.base_indicator import BaseIndicator

engine = database.engine
conn = engine.connect()

class VolumeChangeMonitor(BaseIndicator):
    def __init__(self, market, interval):
        super(VolumeChangeMonitor, self).__init__(market, interval, 2)
        self.write_strategy_description_to_db()
        self.__previous_volume = 0
        self.close = None
        self.timestamp = None
        self.value = None

    def next_calculation(self, candle):
        """get latest N candles from market, do calculation, write results to db"""
        self.do_calculation(candle)
        self.write_ta_statistic_to_db(candle)
        print("Calculated new volume change: " + str(self.value))

    def do_calculation(self, candle):
        new_volume = candle[5]
        if self.__previous_volume is not 0:
            self.value = round(100 * ((new_volume - self.__previous_volume)/self.__previous_volume), 2)  # calculate change in volume in percentage terms
        self.__previous_volume = new_volume
        self.timestamp = ohlcv_functions.convert_timestamp_to_date(candle[0])
        self.close = candle[4]

    def write_ta_statistic_to_db(self, candle):
        """Inserts average into table"""
        with database.lock:
                ins = database.TAVolumeChange.insert().values(Exchange=self.market.exchange.id, Pair=self.market.analysis_pair, Time=self.timestamp, Volume=self.__previous_volume, Interval=self.periods, PercentVolumeChange=self.value, TimestampRaw=candle[0])
                conn.execute(ins)
                print('Wrote statistic to db...')

    def write_strategy_description_to_db(self):
        '''Add ID and description to TAIdentifier table'''
        with database.lock:
            ins = database.TAIdentifier.insert().values(Description='Keeps track of volume changes between each period')
            conn.execute(ins)
