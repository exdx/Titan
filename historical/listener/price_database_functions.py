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

    if create_price_db.conn is not None:
        execute_sql(create_price_db.conn, sql_create_ohlcv_table)
        execute_sql(create_price_db.conn, sql_create_pairs_table)
    else:
        print("Error! cannot create the database connection.")


def insert_data_into_ohlcv_table(candle):
    c = create_price_db.conn.cursor()
    if create_price_db.conn is not None:
        c.execute(insert_data_into_ohlcv_table_sql, candle[0], candle[1], candle[2], candle[3], candle[4], candle[5])
    create_price_db.conn.commit()
    print("Writing price data successfully")


def has_candle(candle_data, exchange, interval):
    c = create_price_db.conn.cursor()
    c.execute(get_latest_candle, exchange, interval)
    row = c.fetchone()
    if (row['timestamp'] == candle_data[0]):
        return True
    else:
        return False


