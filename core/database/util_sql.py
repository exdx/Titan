#Utility SQL Section for drop/create tables upon entering program only

sql_drop_ohlcv = """DROP TABLE IF EXISTS OHLCV;"""

sql_drop_pairs = """DROP TABLE IF EXISTS pairs;"""

sql_drop_ta_identifier = """DROP TABLE IF EXISTS ta_identifier;"""

sql_drop_ta_det_x1 = """DROP TABLE IF EXISTS ta_det_x1;"""

sql_create_ohlcv_table = """ CREATE TABLE IF NOT EXISTS OHLCV (
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

sql_create_ta_identifier_table = """CREATE TABLE IF NOT EXISTS ta_identifier (
                                    ta_id integer PRIMARY KEY,
                                    description text
                                     ); """

sql_create_ta_det_x1_table = """CREATE TABLE IF NOT EXISTS ta_det_x1 (
                                    ta_id integer,
                                    ta_det_id integer PRIMARY KEY,
                                    pair text,
                                    time date,
                                    CLOSE float,
                                    SMA_SLOW_INTERVAL integer,
                                    SMA_SLOW float,
                                    SMA_FAST_INTERVAL integer,
                                    SMA_FAST float,
                                    VOLUME_CHANGE float
                                    ); """
