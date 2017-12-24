from core.markets import exchange
from core.database import connection_manager
import time


def main():
    print("Running...")
    print("Market 1 instantiated...")
    ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC', '5m')
    print("Market 2 instantiated...")
    LTC_BTC_Exchange = exchange.Market('bittrex', 'LTC', 'BTC', '5m')
    print("Loading Candles...")
    # running this 'ticker' from the main loop to trigger listeners to pull candles each minute
    while True:
        """Running this 'ticker' from the main loop to trigger listeners to pull candles each minute"""
        """Only 55 seconds to stay ahead of the clock (since we have logic to assure no duplicates added)"""
        exchange.update_all_candles()
        time.sleep(59)  #



# wipe and recreate tables
connection_manager.reset_db()

# run main
main()


