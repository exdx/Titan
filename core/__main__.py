from core.listener import market_listener
from core.markets import exchange
from core.database import connection_manager
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC', '1m')
    print("Market 2 instantiated...")
    LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC', '1m')
    print("Loading Candles...")
    market_listener.load_historical()

    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles each minute"""
        """Only 55 seconds to stay ahead of the clock (since we have logic to assure no duplicates added)"""
        market_listener.tick_all()
        time.sleep(55)


# wipe and recreate tables
connection_manager.reset_db()

# run main
main()


