import ccxt
from core.markets import exchange
from core.database import connection_manager


#Step one create price database
connection_manager.reset_db() #for debug

#Step two initialize exchange class
ETH_BTC_Exchange = exchange.Market('bittrex', 'ETH', 'BTC')








