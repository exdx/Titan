from core.database import database
from sqlalchemy.sql import select, and_
import pandas as pd
import datetime


engine = database.engine
conn = engine.connect()


def insert_data_into_ohlcv_table(exchange, pair, interval, candle):
    """Inserts exchange candle data into table"""
    with database.lock:
        args = [exchange, pair, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval]
        ins = database.OHLCV.insert().values(Exchange=args[0], Pair=args[1], Timestamp=convert_timestamp_to_date(args[2]), Open=args[3], High=args[4], Low=args[5], Close=args[6], Volume=args[7], Interval=args[8], TimestampRaw=args[2])
        conn.execute(ins)
        print('Adding candle with timestamp: ' + str(candle[0]))



def get_latest_candle(exchange, pair, interval):
    """Returns only latest candle if it exists, otherwise returns 0"""
    s = select([database.OHLCV]).where(and_(database.OHLCV.c.Exchange == exchange, database.OHLCV.c.Pair == pair, database.OHLCV.c.Interval == interval)).order_by(database.OHLCV.c.ID.desc()).limit(1)
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    return row

def get_all_candles(exchange, pair, interval):
    s = select([database.OHLCV]).where(and_(database.OHLCV.c.Exchange == exchange, database.OHLCV.c.Pair == pair,
                                            database.OHLCV.c.Interval == interval))
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    return row

def get_latest_N_candles_as_df(exchange, pair, interval, N):
    """Returns N latest candles for TA calculation purposes"""
    s = select([database.OHLCV]).where(and_(database.OHLCV.c.Exchange == exchange, database.OHLCV.c.Pair == pair, database.OHLCV.c.Interval == interval)).order_by(database.OHLCV.c.ID.desc()).limit(N)
    result = conn.execute(s)
    df = pd.DataFrame(result.fetchall())
    df.columns = result.keys()
    result.close()
    return df

def get_historical_ta_data_as_df():
    s = select([database.TAMovingAverage]).order_by(database.TAMovingAverage.c.TA_Det_ID.asc())
    result = conn.execute(s)
    df = pd.DataFrame(result.fetchall())
    df.columns = result.keys()
    result.close()
    #historical_ta_data = df['TA_Det_ID', 'Close', 'Interval', 'MovingAverage']
    return df

def has_candle(candle_data, exchange, pair, interval):
    """Checks to see if the candle is already in the historical dataset pulled"""
    print('Checking for candle with timestamp: ' + str(candle_data[0]))

    s = select([database.OHLCV]).where(and_(database.OHLCV.c.Exchange == exchange, database.OHLCV.c.Pair == pair, database.OHLCV.c.Interval == interval)).order_by(database.OHLCV.c.ID.desc()).limit(10)
    result = conn.execute(s)

    for row in result: # limited result to latest 10 entries
        if row[3] == convert_timestamp_to_date(candle_data[0]) and row[1] == exchange and row[2] == pair:  # compare timestamp of database row to timestamp of candle data passed in
            return True
    result.close()
    return False


def write_trade_pairs_to_db(PairID, Base, Quote):
    with database.lock:
        ins = database.TradingPairs.insert().values(PairID=PairID, BaseCurrency=Base, QuoteCurrency=Quote)
        conn.execute(ins)


def convert_timestamp_to_date(timestamp):
    value = datetime.datetime.fromtimestamp(float(str(timestamp)[:-3]))  #this might only work on bittrex candle timestamps
    return value.strftime('%Y-%m-%d %H:%M:%S')

