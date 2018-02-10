from threading import Thread
from pubsub import pub
from core.markets import market
from core.markets import market_watcher
from strategies import base_strategy
import time
import logging

logger = logging.getLogger(__name__)

tickers = {}


def subscribe(tick_callable, interval):
    start_ticker(interval)
    pub.subscribe(tick_callable, "tick" + interval)

def start_ticker(interval):
    """Start a ticker/timer that notifies market watchers when to pull a new candle"""
    if interval not in tickers:
        tickers[interval] = Thread(target=__start_ticker, args=(interval,)).start()


def __start_ticker(interval):
    """Start a ticker own its own thread, will use pypubsub to send a message each time interval"""
    logger.info(interval + " ticker running...")
    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles every 5 minutes"""
        logger.info("Live Tick: {}".format(str(live_tick_count)))
        print(interval + " tick")
        pub.sendMessage("tick" + interval)
        live_tick_count += 1
        time.sleep(__convert_interval_to_int(interval))  # wait 5 minutes


def __convert_interval_to_int(interval):
    if interval == "5m":
        return 300
    if interval == "1m":
        return 60
    if interval == "1h":
        return 3600
