from core.database import connection_manager
from sqlalchemy.sql import select, and_
import pandas as pd
import datetime
from sqlalchemy.sql import select
from threading import Lock

engine = connection_manager.engine
conn = engine.connect()
lock = Lock()

def insert_data_into_ohlcv_table(exchange, pair, interval, candle):
    '''Inserts exchange candle data into table'''
    with lock:
        args = [exchange, pair, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval]
        ins = connection_manager.OHLCV.insert().values(Exchange=args[0], Pair=args[1], Timestamp=convert_timestamp_to_date(args[2]), Open=args[3], High=args[4], Low=args[5], Close=args[6],Volume=args[7],Interval=args[8])
        conn.execute(ins)
        print('Adding candle with timestamp: ' + str(candle[0]))


def get_latest_candle(exchange, pair, interval):
    '''Returns only latest candle if it exists, otherwise returns 0'''
    s = select([connection_manager.OHLCV]).where(and_(connection_manager.OHLCV.c.Exchange == exchange,connection_manager.OHLCV.c.Pair == pair,connection_manager.OHLCV.c.Interval == interval)).order_by(connection_manager.OHLCV.c.ID.desc()).limit(1)
    result = conn.execute(s)
    row = result.fetchone()
    return row if (row != None) else 0
    result.close()

def get_latest_N_candles_as_df(exchange, pair, interval, N):
    '''Returns N latest candles for TA calculation purposes'''
    s = select([connection_manager.OHLCV]).where(and_(connection_manager.OHLCV.c.Exchange == exchange,connection_manager.OHLCV.c.Pair == pair,connection_manager.OHLCV.c.Interval == interval)).order_by(connection_manager.OHLCV.c.ID.desc()).limit(N)
    result = conn.execute(s)
    df = pd.DataFrame(result.fetchall())
    df.columns = result.keys()
    return(df)


def has_candle(candle_data, exchange, pair, interval):
    '''Checks to see if the candle is already in the historical dataset pulled'''
    print('Checking for candle with timestamp: ' + str(candle_data[0]))

    s = select([connection_manager.OHLCV]).where(and_(connection_manager.OHLCV.c.Exchange == exchange,connection_manager.OHLCV.c.Pair == pair,connection_manager.OHLCV.c.Interval == interval))
    result = conn.execute(s)

    for row in result: # now that we are using multiple listeners, loop through all candles (will need to refactor for optimization to loop through only a number of the latest)
        if row[3] == candle_data[0] and row[1] == exchange and row[2] == pair:  # compare timestamp of database row to timestamp of candle data passed in
            return True
    return False


def convert_timestamp_to_date(timestamp):
    print("Converting " + str(timestamp) + " to timestamp")
    value = datetime.datetime.fromtimestamp(float(str(timestamp)[:-3]))
    print("Converted to " + str(value))
    return value.strftime('%Y-%m-%d %H:%M:%S')

