from threading import Thread
from pubsub import pub
from core.markets import market
from core.markets import market_watcher
from strategies import base_strategy
import time
import logging

logger = logging.getLogger(__name__)

tickers = {}


def start_ticker(interval):
    if interval not in tickers:
        tickers[interval] = Thread(target=__start_ticker, args=(interval,)).start()


def __start_ticker(interval):
    logger.info(interval + " ticker running...")
    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles every 5 minutes"""
        logger.info("Live Tick: {}".format(str(live_tick_count)))
        pub.sendMessage("tick" + interval)
        live_tick_count += 1
        time.sleep(__convert_interval_to_int(interval))  # wait 5 minutes


def __convert_interval_to_int(interval):
    if interval == "5m":
        return 300
