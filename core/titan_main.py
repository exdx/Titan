from core.database import database
from strategies import poc_strategy
from time import sleep
import logging

logger = logging.getLogger(__name__)



def start_strategy(user_input):

    # strategy = poc_strategy.PocStrategy("5m", 'bittrex', 'ETH', 'BTC', 100, 700, True, sim_balance=10)
    # strategy2 = poc_strategy.PocStrategy("5m", 'binance', 'ETH', 'BTC', 233, 900, True, sim_balance=10)

    strategy = poc_strategy.PocStrategy(user_input[3], user_input[0], user_input[1], user_input[2], user_input[6], user_input[5], user_input[4], user_input[7]) # if test strategy button clicked

    strategy.run_simulation()
    strategy.start()


def start_database():
    database.create_tables()

# For running app headless
def start():
    try:
        # wipe and recreate tables
        database.create_tables()

        start_strategy()

    except Exception as e:
        print(e)

    finally:
        database.engine.dispose()


if __name__ == "__main__":
    start()
