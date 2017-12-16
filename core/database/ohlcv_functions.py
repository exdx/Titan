import os
import sqlite3
from sqlite3 import Error
from core.database import ohlcv_SQL
from core.database import connection_manager

database = connection_manager

def insert_data_into_ohlcv_table(candle_id, exchange, interval, candle):
    args = (candle_id, exchange, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval,)
    database.execute_sql(ohlcv_SQL.insert_data_into_ohlcv_table_sql, args)
    print('Candle Timestamp: ' + str(candle[0]))

def clear_ohlcv_table():
    database.execute_sql('delete from OHLCV;')

def get_latest_candle_id(exchange, interval):
    args = (exchange, interval,)
    row = database.execute_query(ohlcv_SQL.get_latest_candle, args)
    return row[0] if (row != None) else 0

def has_candle(candle_data, exchange, interval):
    args = (exchange, interval, )
    row = database.execute_query(ohlcv_SQL.get_latest_candle, args)
    if row[0] == candle_data:
        return True
    else:
        return False