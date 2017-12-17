sql_drop_ohlcv = """DROP TABLE OHLCV;"""

sql_drop_pairs = """DROP TABLE pairs;"""

sql_create_ohlcv_table = """ CREATE TABLE IF NOT EXISTS OHLCV (
                                    datetime text,
                                    exchange text,
                                    pair text,
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