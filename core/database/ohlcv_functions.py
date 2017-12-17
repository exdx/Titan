import datetime
from core.database import ohlcv_sql
from core.database import connection_manager

database = connection_manager


def insert_data_into_ohlcv_table(exchange, pair, interval, candle):
    args = (convert_timestamp_to_date(candle[0]), exchange, pair, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval,)
    database.execute_sql(ohlcv_sql.insert_data_into_ohlcv_table_sql, args)
    print('Candle Timestamp: ' + str(candle[0]))


def clear_ohlcv_table():
    database.execute_sql('delete from OHLCV;')


def get_latest_candle_time(exchange, pair, interval):
    args = (exchange, pair, interval,)
    row = database.execute_query(ohlcv_sql.get_candles, args)[0]
    print(row[0])
    return row[0] if (row != None) else 0


def has_candle(candle_data, exchange, pair, interval):
    args = (exchange, pair, interval,)
    row = database.execute_query(ohlcv_sql.get_candles, args)[0]
    print(row)
    print(candle_data)
    if row[3] == candle_data[0]:  # compare timestamp of database row to timestamp of candle data passed in
        return True
    else:
        return False


def convert_timestamp_to_date(timestamp):
    print(timestamp)
    #converted_timestamp = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    #print(converted_timestamp)
    #return converted_timestamp
    return "1"