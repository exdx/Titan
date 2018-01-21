from threading import Thread
from core.markets import market
from core.markets import position_manager
from strategies import base_strategy
import time

tickers = {}


def start_ticker(interval):
    if tickers.get(interval) is None:
        tickers[interval] = Thread(target=__start_ticker, args=(interval,))


def __start_ticker(interval):
    print( interval + " ticker running...")
    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles every 5 minutes"""
        print("Live Tick: {}".format(str(live_tick_count)))
        market.update_all_candles(interval)
        base_strategy.update_all_strategies(interval)
        print('Pulled 5m candle #{}. Waiting for next live candle...'.format(
            str(live_tick_count)))
        live_tick_count += 1
        time.sleep(__convert_interval_to_int(interval))  # wait 5 minutes


def __convert_interval_to_int(interval):
    if interval == "5m":
        return 300
