import os
import numpy as np
import pandas as pd
import pickle
import quandl
from datetime import datetime

#Get BTC historical data
#Credit to work done by Patrick Triest

def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

# Pull pricing data for top BTC exchanges into dictionary
exchanges = ['COINBASE','BITSTAMP','ITBIT', 'KRAKEN']
exchange_data = {}

for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df

def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]

    return pd.DataFrame(series_dict)




#Create dataframe containing data from multiple exchanges for both price and volume
btc_usd_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')
btc_usd_datasets = btc_usd_datasets.rename(columns={'BITSTAMP': 'BITSTAMP_PRICE', 'COINBASE': 'COINBASE_PRICE', 'ITBIT': 'ITBIT_PRICE', 'KRAKEN': 'KRAKEN_PRICE'})

btc_usd_BTCvolume_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Volume (BTC)')
btc_usd_BTCvolume_datasets = btc_usd_BTCvolume_datasets.rename(columns={'BITSTAMP': 'BITSTAMP_BTCVOLUME', 'COINBASE': 'COINBASE_BTCVOLUME', 'ITBIT': 'ITBIT_BTCVOLUME', 'KRAKEN': 'KRAKEN_BTCVOLUME'})

btc_usd_CURRENCYvolume_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Volume (Currency)')
btc_usd_CURRENCYvolume_datasets = btc_usd_CURRENCYvolume_datasets.rename(columns={'BITSTAMP': 'BITSTAMP_CURRENCYVOLUME', 'COINBASE': 'COINBASE_CURRENCYVOLUME', 'ITBIT': 'ITBIT_CURRENCYVOLUME', 'KRAKEN': 'KRAKEN_CURRENCYVOLUME'})

#Clean dataframes by removing zeroes (exchange outages)

btc_usd_datasets.replace(0, np.nan, inplace=True)
btc_usd_BTCvolume_datasets.replace(0, np.nan, inplace=True)
btc_usd_CURRENCYvolume_datasets.replace(0, np.nan, inplace=True)

#Arrive at one historical value by averaging across the different exchanges
btc_usd_datasets['AVERAGE_BTC_USD_PRICE'] = btc_usd_datasets.mean(axis=1)
btc_usd_BTCvolume_datasets['AVERAGE_BTC_VOLUME'] = btc_usd_BTCvolume_datasets.mean(axis=1)
btc_usd_CURRENCYvolume_datasets['AVERAGE_BTC_CURRENCY_VOLUME'] = btc_usd_CURRENCYvolume_datasets.mean(axis=1)

#reset indexes to use in merge
btc_usd_datasets_indexed = btc_usd_datasets.reset_index()
btc_usd_BTCvolume_datasets_indexed = btc_usd_BTCvolume_datasets.reset_index()
btc_usd_CURRENCYvolume_datasets_indexed = btc_usd_CURRENCYvolume_datasets.reset_index()

#create combined, final result
historical_btc_df = btc_usd_CURRENCYvolume_datasets_indexed.merge(btc_usd_datasets_indexed.merge(btc_usd_BTCvolume_datasets_indexed,how='inner',on='Date'), how='inner', on='Date')
historical_btc_df_final = historical_btc_df[['Date','AVERAGE_BTC_USD_PRICE','AVERAGE_BTC_VOLUME','AVERAGE_BTC_CURRENCY_VOLUME']]

#print(historical_btc_df_final)

