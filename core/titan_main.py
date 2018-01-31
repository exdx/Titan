from core.database import database
from strategies import poc_strategy
from core.markets import ticker
import json
import titan_app


def main(user_input):

    strategy = poc_strategy.PocStrategy(user_input[3], user_input[0], user_input[1], user_input[2], user_input[4]) # if test strategy button clicked
    #strategy = poc_strategy.PocStrategy(user_input[3], user_input[0], user_input[1], user_input[2],False )  if real strategy button clicked

    strategy.start()
    ticker.start_ticker(user_input[3])



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


