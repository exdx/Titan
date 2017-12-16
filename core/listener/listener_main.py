import ccxt
import core.markets
import core.database
from core.database import connection_manager


#Step one create price database
connection_manager.reset_db() #for debug

#Step two initialize exchange class
ETH_BTC_Exchange = Market('bittrex','ETH','BTC')

#Step three write data into database
ETH_BTC_Exchange.pull_OHLCV_data(59, '1m')








