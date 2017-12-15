##SQL Queries to initialize tables

sql_drop_ohlcv = """DROP TABLE OHLCV;"""

sql_drop_pairs = """DROP TABLE pairs;"""

sql_create_ohlcv_table = """ CREATE TABLE IF NOT EXISTS OHLCV (
                                    unique_id integer PRIMARY KEY,
                                    exchange text,
                                    timestamp integer,
                                    open float,
                                    high float,
                                    low float,
                                    close float,
                                    volume float,
                                    interval text
                                ); """


sql_create_pairs_table = """ CREATE TABLE IF NOT EXISTS pairs (
                                    unique_id integer PRIMARY KEY,
                                    base_currency text,
                                    quote_currency text
                                    ); """


# Parameters: unique_id, exchange, timestamp, open, high, low, close, volume, interval
insert_data_into_ohlcv_table_sql = """INSERT INTO OHLCV (unique_id, exchange, timestamp, open, high, low, close, volume, interval) 
                                            VALUES(?,?,?,?,?,?,?,?,?);"""


# Parameters: exchange.id, interval
get_latest_candle = """SELECT * FROM OHLCV 
                    WHERE exchange = ? AND 
                     interval = ? AND 
                     unique_id = (SELECT MAX(unique_id) FROM OHLCV);"""
