# Parameters: unique_id, exchange, timestamp, open, high, low, close, volume, interval
insert_data_into_ohlcv_table_sql = """INSERT INTO OHLCV (unique_id, exchange, timestamp, open, high, low, close, volume, interval) 
                                            VALUES(?,?,?,?,?,?,?,?,?);"""


# Parameters: exchange.id, interval
get_latest_candle = """SELECT timestamp, open, high, low, close, volume FROM OHLCV 
                    WHERE exchange = ? AND 
                     interval = ? AND 
                     unique_id = (SELECT MAX(unique_id) FROM OHLCV);"""

get_latest_candle_id = """SELECT MAX(unique_id) FROM OHLCV 
                    WHERE exchange = ? AND 
                     interval = ?;"""