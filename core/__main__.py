from core.markets import market
from core.markets import market_simulator
from core.database import database
from strategies import sma_crossover_strategy
import time
from core.markets import position_manager

def main():

    print("Instantiating crossover strategy")
    sma_crossover_strategy.SmaCrossoverStrategy(100, 770)


    print("5m ticker running...")
    live_tick_count = 0
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles every 5 minutes"""
        print("Live Tick: {}".format(str(live_tick_count)))
        market.update_all_candles('5m')
        position_manager.update_all_positions()
        print('Wrote live 5m candle #{} to DB and calculated moving average. Waiting for next live candle...'.format(str(live_tick_count)))
        live_tick_count += 1
        time.sleep(300)  # wait 5 minutes


if __name__ == '__main__':
    try:
        # wipe and recreate tables
        database.reset_db()

        # run main
        main()

    except Exception as e:
        print(e)

    finally:
        database.engine.dispose()


