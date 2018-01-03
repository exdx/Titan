from core.markets import market
from core.database import connection_manager
from strategies import ema_crossover_strategy
from ta import simple_moving_average
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = market.Market('bittrex', 'ETH', 'BTC')
#    print("Market 2 instantiated...")
#    LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC')
#    print("Loading Candles...")
    ETH_BTC_Exchange.apply_strategy(ema_crossover_strategy.CrossoverStrategy())

    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles each minute"""
        print("Live Tick: {}".format(str(live_tick_count)))
        market.update_all_candles(live_tick_count)

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


