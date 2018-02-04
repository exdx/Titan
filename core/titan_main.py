from core.database import database
from strategies import poc_strategy
from time import sleep
import logging

logger = logging.getLogger(__name__)


def main(user_input):

    # strategy = poc_strategy.PocStrategy("5m", 'bittrex', 'ETH', 'BTC', 100, 700, True, sim_balance=10)
    # strategy2 = poc_strategy.PocStrategy("5m", 'binance', 'ETH', 'BTC', 233, 900, True, sim_balance=10)

    strategy = poc_strategy.PocStrategy(user_input[3], user_input[0], user_input[1], user_input[2], 100, 700, user_input[4], sim_balance=10) # if test strategy button clicked
    #strategy = poc_strategy.PocStrategy(user_input[3], user_input[0], user_input[1], user_input[2],False )  if real strategy button clicked
    strategy.run_simulation()
    strategy.start()


def reset_db():
    try:
        # wipe and recreate tables
        database.reset_db()

    except Exception as e:
        print(e)

    finally:
        database.engine.dispose()


