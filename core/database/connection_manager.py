import os
import sqlite3
from sqlite3 import Error
from core.database import util_SQL

db_name = 'core_db.db'
db_fullpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), db_name)

def execute_sql(sql_string, args):
    if args:
        try:
            conn = sqlite3.connect(db_fullpath)
            c = conn.cursor()
            c.execute(sql_string, args)
            conn.commit()
            conn.close()
        except Error as e:
            print(e)
    else:
        try:
            conn = sqlite3.connect(db_fullpath)
            c = conn.cursor()
            c.execute(sql_string)
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

def execute_query(sql_string, args):
    if args:
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
    else:
        try:
            conn = sqlite3.connect(db_fullpath)
            c = conn.cursor()
            c.execute(sql_string)
            data = c.fetchall()
            conn.commit()
            conn.close()
            return data
        except Error as e:
            print(e)


def reset_db():
    print('Resetting tables')
    execute_sql(util_SQL.sql_drop_ohlcv, None)
    execute_sql(util_SQL.sql_drop_pairs, None)


def create_tables():
    print('Creating tables')
    execute_sql(util_SQL.sql_create_ohlcv_table, None)
    execute_sql(util_SQL.sql_create_pairs_table, None)