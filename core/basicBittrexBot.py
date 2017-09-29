#bittrex

from bittrex import bittrex

key_secret_pair = ('x', 'y') 

api = bittrex(key_secret_pair)

print api.getticker('BTC-ETH')

trade = 'BTC'
currency = 'ETH'
market = '{0}-{1}'.format(trade, currency)
amount = 1
multiplier = 1.1

#print api.getmarketsummary(market)


btc_eth_summary = api.getmarketsummary(market)
eth_price = btc_eth_summary[0]['Last']

print ('The price for {0} is {1:.8f} {2}.'.format(currency, eth_price, trade))

#send buy order
print ('Buying {0} {1} for {2:.8f} {3}.'.format(amount, currency, eth_price, trade))
#api.buylimit(market, amount, eth_price)

# Multiplying the price by the multiplier
eth_price = round(eth_price*multiplier, 8)

# Selling for the  new price
print ('Selling {0} {1} for {2:.8f} {3}.'.format(amount, currency, eth_price, trade))
#api.selllimit(market, amount, eth_price)

# Gets the ETH balance
#~ eth_balance = api.getbalance(currency)
#~ print ("Your balance is {0} {1}.".format(eth_balance['Available'], currency))
