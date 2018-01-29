from core.database import database
from strategies import poc_strategy
from core.markets import ticker
from core.markets import market
from core.markets import market_simulator


def main():

    strategy = poc_strategy.PocStrategy("5m", 'bittrex', 'ETH', 'BTC', 100, 700, True, sim_balance=10)
    strategy2 = poc_strategy.PocStrategy("5m", 'binance', 'ETH', 'BTC', 233, 900, True, sim_balance=10)
    strategy.start()
    strategy2.start()


def start():
    try:
        # wipe and recreate tables
        database.reset_db()

        main()

    except Exception as e:
        print(e)

    finally:
        database.engine.dispose()

if __name__ == "__main__":
    start()
