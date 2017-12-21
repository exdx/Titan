from ta.ta_sql import get_latest_candle
from core.database.connection_manager import execute_query


def pull_latest_candle_data_from_OHLCV(exchange, pair, interval):
        args = (exchange, pair, interval,)
        row = execute_query(get_latest_candle, args)
        return row #something