# Parameters: unique_id, exchange, timestamp, open, high, low, close, volume, interval
insert_data_into_ohlcv_table_sql = """INSERT INTO OHLCV (datetime, exchange, pair, timestamp, open, high, low, close, volume, interval) 
                                            VALUES(?,?,?,?,?,?,?,?,?,?);"""


get_candles = """SELECT * FROM OHLCV 
                    WHERE exchange = ? AND
                     pair = ? AND 
                     interval = ?"""