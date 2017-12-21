
insert_data_into_ta_det_x1_sql = """INSERT INTO ta_identifier (ta_id, description) 
                                            VALUES('1','A basic momentum based TA strategy')"""



insert_data_into_ta_det_x1_sql = """INSERT INTO ta_det_x1 (ta_id, ta_det_id, pair, time, CLOSE,SMA_SLOW_INTERVAL,SMA_SLOW,SMA_FAST_INTERVAL,SMA_FAST,VOLUME_CHANGE) 
                                            VALUES('1','1',?, 
                                            SELECT strftime('%Y-%m', timestamp / 1000, 'unixepoch') FROM OHLCV,
                                            7,7,7,7,7,7,7,7,7);"""

get_latest_candle = """SELECT * FROM OHLCV 
                        WHERE exchange = ? AND
                        pair = ? AND 
                        interval = ?
               
                        ORDER BY timestamp DESC
               
                        LIMIT 1;"""

#This is the convert datetime function

#SELECT DATETIME( timestamp / 1000, 'unixepoch') as time FROM OHLCV