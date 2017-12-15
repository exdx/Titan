import os
import sqlite3
from sqlite3 import Error
from price_database_SQL import *

db_name = 'titan_price_history_db.db'


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def execute_sql(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def create_price_db():
    create_price_db.database = os.path.join(os.path.dirname(os.path.realpath(__file__)),db_name)
    create_price_db.conn = create_connection(create_price_db.database)

    #drop tables
    execute_sql(create_price_db.conn, sql_drop_ohlcv)
    execute_sql(create_price_db.conn, sql_drop_pairs)
    #for debug


    execute_sql(create_price_db.conn, sql_create_ohlcv_table)
    execute_sql(create_price_db.conn, sql_create_pairs_table)

   # else:
    #    print("Error! cannot create the database connection.")


def insert_data_into_ohlcv_table(candle_id, exchange, interval, candle):
    c = create_price_db.conn.cursor()
    if create_price_db.conn is not None:
        args = (candle_id, exchange, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], interval,)
        c.execute(insert_data_into_ohlcv_table_sql, args)
    create_price_db.conn.commit()
    print('Candle Timestamp: ' + str(candle[0]))

def clear_ohlcv_table():
    c = create_price_db.conn.cursor()
    c.execute('delete from OHLCV;')
    create_price_db.conn.commit()

def has_candle(candle_data, exchange, interval):
    c = create_price_db.conn.cursor()
    args = (exchange, interval, )
    c.execute(get_latest_candle, args)
    row = c.fetchone()
    print(row)
    if (row[0] == candle_data[0]):
        return True
    else:
        return False


