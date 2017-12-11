##SQL Queries to initialize tables

sql_create_ohlcv_table = """ CREATE TABLE IF NOT EXISTS OHLCV (
                                    unique_id integer PRIMARY KEY,
                                    pair_id integer,
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
