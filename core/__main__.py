from core.markets import market
from core.database import database
from strategies import sma_crossover_strategy
from ta import simple_moving_average
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = market.Market('bittrex', 'ETH', 'BTC')
    ETH_BTC_Exchange.apply_strategy(sma_crossover_strategy.SmaCrossoverStrategy(ETH_BTC_Exchange))

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
    database.reset_db()

    # run main
    main()

except Exception as e:
    print(e)

finally:
    database.engine.dispose()


