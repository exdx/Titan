import os
import sqlite3
from sqlite3 import Error
from util_SQL import *

db_name = 'core_db.db'
db_fullpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), db_name)


def execute_sql(sql_string):
    try:
        conn = sqlite3.connect(db_fullpath)
        c = conn.cursor()
        c.execute(sql_string)
        conn.commit()
        conn.close()
    except Error as e:
        print(e)


def execute_sql(sql_string, args):
    try:
        conn = sqlite3.connect(db_fullpath)
        c = conn.cursor()
        c.execute(sql_string, args)
        conn.commit()
        conn.close()
    except Error as e:
        print(e)

def execute_query(sql_string, args):
    try:
        conn = sqlite3.connect(db_fullpath)
        c = conn.cursor()
        c.execute(sql_string, args)
        data = c.fetchall()
        conn.commit()
        conn.close()
        return data
    except Error as e:
        print(e)


def reset_db():
    print('Resetting tables')
    try:
        execute_sql(create_price_db.conn, sql_drop_ohlcv)
        execute_sql(create_price_db.conn, sql_drop_pairs)
    except:
        print('No tables exist')

    execute_sql(create_price_db.conn, sql_create_ohlcv_table)
    execute_sql(create_price_db.conn, sql_create_pairs_table)