from core.database import connection_manager
from sqlalchemy.sql import select

engine = connection_manager.engine
conn = engine.connect()

def insert_data_into_ohlcv_table(exchange, pair, interval, candle):
    args = [exchange, pair, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval]
    ins = connection_manager.OHLCV.insert().values(Exchange=args[0], Pair=args[1], Timestamp=args[2], Open=args[3], High=args[4], Low=args[5], Close=args[6],Volume=args[7],Interval=args[8])
    conn.execute(ins)
    print('Adding candle with timestamp: ' + str(candle[0]))


def has_candle(candle_data, exchange, pair, interval):
    print('Checking for candle with timestamp: ' + str(candle_data[0]))
    args = (exchange, pair, interval,)

    s = select([connection_manager.OHLCV])
    candles = conn.execute(s)
    for row in candles: # now that we are using multiple listeners, loop through all candles (will need to refactor for optimization to loop through only a number of the latest)
        if row[3] == candle_data[0] and row[1] == exchange and row[2] == pair:  # compare timestamp of database row to timestamp of candle data passed in
            return True
    return False


def convert_timestamp_to_date():
    pass

