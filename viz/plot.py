import matplotlib.pyplot as plt
from core.database import ohlcv_functions

#Library to explore visualization of API data. Critical to ensure data integrity as well as confirm strategy indicators are calculated correctly .

class BasePlot:
    def __init__(self, exchange, pair, interval, N_candles):
        self.exchange = exchange
        self.pair = pair
        self.interval = interval
        self.N_candles = N_candles

    def basic_plot(self):
        '''Make basic matplotlib line chart with close on the Y axis'''
        latest_N_ohlcv_candles = ohlcv_functions.get_latest_N_candles_as_df(self.exchange, self.pair, self.interval, self.N_candles)
        close = latest_N_ohlcv_candles['Close'].tolist()

        plt.plot(close)
        plt.show()

Plot = BasePlot('bittrex', 'ETH/BTC', '1m', 50)
Plot.basic_plot()

