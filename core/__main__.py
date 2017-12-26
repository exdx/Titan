from core.markets import exchange
from core.database import connection_manager
from ta import ta_functions
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC')
 #   print("Market 2 instantiated...")
  #  LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC')

    ETH_BTC_Exchange.apply_indicator(ta_functions.SimpleMovingAverage("5m", 1440, ETH_BTC_Exchange, 'slow'))
    ETH_BTC_Exchange.apply_indicator(ta_functions.SimpleMovingAverage("5m", 12, ETH_BTC_Exchange, 'fast'))

    print("Loading Candles...")


    # running this 'ticker' from the main loop to trigger listeners to pull candles each minute
    minutes_running = 1
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles each minute"""
        """Only 55 seconds to stay ahead of the clock (since we have logic to assure no duplicates added)"""
        print("Tick: " + str(minutes_running))
        exchange.update_all_candles(minutes_running)
        time.sleep(60)
        minutes_running += 1


# wipe and recreate tables
connection_manager.reset_db()

# run main
main()


