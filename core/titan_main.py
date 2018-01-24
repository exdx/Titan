from core.database import database
from strategies import poc_strategy
from core.markets import ticker
from core.markets import market
from core.markets import market_simulator


def main():

    strategy = poc_strategy.PocStrategy("5m", 'bittrex', 'ETH', 'BTC', True)
    strategy.start()
    ticker.start_ticker(strategy.interval)

    while True:
        """Program is running"""


def start():
    try:
        # wipe and recreate tables
        database.reset_db()

        # run main
        main()

    except Exception as e:
        print(e)

    finally:
        database.engine.dispose()


