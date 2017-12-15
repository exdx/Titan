import ccxt
from initialize_ccxt import Exchange
from price_database_functions import *


#Step one create price database
create_price_db()

#Step two initialize exchange class
ETH_BTC_Exchange = Exchange('bittrex','ETH','BTC')

#Step three write data into database
ETH_BTC_Exchange.pull_OHLCV_data(59,'1m')








