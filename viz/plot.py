import matplotlib.pyplot as plt
from core.database import ohlcv_functions
import pandas as pd
from core.markets import market

# Library to explore visualization of API data. Critical to ensure data integrity as well as confirm strategy indicators are calculated correctly .


def historical_ta_plot(historical_status):
    """Make basic matplotlib line chart with close and moving averages on the Y axis for historical data and new candles"""
    if historical_status:
        data = ohlcv_functions.get_historical_ta_data_as_df()
        data.groupby('Interval').plot(x='TA_Det_ID', y=['Close', 'MovingAverage'])
        plt.show()


historical_ta_plot(True)



