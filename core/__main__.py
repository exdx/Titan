from core.markets import exchange
from core.database import connection_manager
from ta import ta_functions
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC')
#   print("Market 2 instantiated...")
#   LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC')

    print("Loading Candles...")

    ETH_BTC_Exchange.apply_indicator(ta_functions.SimpleMovingAverage(ETH_BTC_Exchange, "5m", 1440, 12))

    # running this 'ticker' from the main loop to trigger listeners to pull candles each minute
    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles each minute"""
        """Only 55 seconds to stay ahead of the clock (since we have logic to assure no duplicates added)"""
        print("Live Tick: {}".format(str(live_tick_count)))
        exchange.update_all_candles(live_tick_count)

        print('Wrote live candle #{} to DB and calculated moving average. Waiting for next live candle...'.format(live_tick_count))

        live_tick_count += 1

        time.sleep(300) #idk


try:
    # wipe and recreate tables
    connection_manager.reset_db()

    # run main
    main()

except Exception as e:
    print(e)

finally:
    connection_manager.engine.dispose()


