sql_drop_ta_identifier_table = """DROP TABLE IF EXISTS ta_identifier;"""

sql_drop_ta_det_x1_table = """DROP TABLE IF EXISTS ta_det_x1;"""

sql_create_ta_identifier_table = """CREATE TABLE IF NOT EXISTS ta_identifier (
                                    ta_id integer PRIMARY KEY,
                                    description text,
                                ); """


sql_create_ta_det_x1 = """CREATE TABLE IF NOT EXISTS ta_det_x1 (
                                    ta_id integer,
                                    ta_det_id integer PRIMARY KEY,
                                    pair text,
                                    time date,
                                    LATEST_PRICE_CLOSE float,
                                    SMA_SLOW_INTERVAL integer
                                    SMA_SLOW float,
                                    SMA_FAST_INTERVAL integer,
                                    SMA_FAST float,
                                    VOLUME_CHANGE float
                                    ); """