from core.database import database
from strategies import poc_strategy
from core.markets import ticker
from core.markets import market
from core.markets import market_simulator


def main():

    strategy = poc_strategy.PocStrategy("5m", 'bittrex', 'ETH', 'BTC', True, sim_balance=10)
    strategy.start()

    while True:
        pass

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

if __name__ == "__main__":
    start()
