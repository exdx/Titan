import os
import sqlite3
import threading
from sqlite3 import Error
from core.database import util_sql

db_name = 'core_db.db'
db_fullpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), db_name)

insert_lock = threading.Lock() #thread object that locks the DB so only one thread can write to it at at a time
conn = sqlite3.connect(db_fullpath, check_same_thread=False)

def execute_sql(sql_string, args):
    with insert_lock:
        if args:
            try:
                #conn = sqlite3.connect(db_fullpath)
                c = conn.cursor()
                c.execute(sql_string, args)
                conn.commit()
                #conn.close()
            except Error as e:
                print(e)
        else:
            try:
                #conn = sqlite3.connect(db_fullpath)
                c = conn.cursor()
                c.execute(sql_string)
                conn.commit()
                #conn.close()
            except Error as e:
                print(e)

def execute_query(sql_string, args):
    with insert_lock:
        if args:
            try:
                #conn = sqlite3.connect(db_fullpath)
                c = conn.cursor()
                c.execute(sql_string, args)
                data = c.fetchall()
                conn.commit()
                #conn.close()
                return data
            except Error as e:
                print(e)
        else:
            try:
                #conn = sqlite3.connect(db_fullpath)
                c = conn.cursor()
                c.execute(sql_string)
                data = c.fetchall()
                conn.commit()
                #conn.close()
                return data
            except Error as e:
                print(e)


def drop_tables():
    print('Dropping tables...')
    execute_sql(util_sql.sql_drop_ohlcv, None)
    execute_sql(util_sql.sql_drop_pairs, None)


def create_tables():
    print('Creating tables...')
    execute_sql(util_sql.sql_create_ohlcv_table, None)
    execute_sql(util_sql.sql_create_pairs_table, None)


def reset_db():
    print('Resetting database...')
    drop_tables()
    create_tables()