##SQL to initialize tables for TA

sql_create_atr_table = """ CREATE TABLE IF NOT EXISTS atr (
                                    unique_id integer PRIMARY KEY,
                                    candle_id integer,
                                    FOREIGN KEY(candle_id) REFERENCES OHLCV(unique_id),
                                    atr float"""