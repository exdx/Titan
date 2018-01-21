from core.database import database
from strategies import poc_strategy
from core.markets import ticker

def main():

    strategy = poc_strategy.PocStrategy()
    strategy.start()
    ticker.start_ticker(strategy.interval)

    while True:
        """Program is running"""

if __name__ == '__main__':
    #try:
        # wipe and recreate tables
        database.reset_db()

        # run main
        main()

    #except Exception as e:
        #print(e)

    #finally:
        database.engine.dispose()


