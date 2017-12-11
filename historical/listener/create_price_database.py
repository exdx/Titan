import os
import sqlite3
from sqlite3 import Error
from create_price_database_SQL import sql_create_ohlcv_table, sql_create_pairs_table

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

def main():
    database = os.path.join(os.path.dirname(os.path.realpath(__file__)),db_name)
    conn = create_connection(database)

    if conn is not None:
        execute_sql(conn, sql_create_ohlcv_table)
        execute_sql(conn, sql_create_pairs_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

