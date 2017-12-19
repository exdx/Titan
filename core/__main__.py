from core.listener import market_listener
from core.markets import exchange
from core.database import connection_manager
import time


def main():
    print('Running')
    print("market 1 instantiated")
    ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC')
    print("market 2 instantiated")
    LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC')
    print("loading candles")
    market_listener.load_historical()

    # running this 'ticker' from the main loop to trigger listeners to pull candles each minute
    while True:
        market_listener.tick_all()
        time.sleep(59)  #


# wipe and recreate tables
connection_manager.reset_db()

# run main
main()


