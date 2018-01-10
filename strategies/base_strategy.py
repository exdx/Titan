class BaseStrategy:
    """Defines an abstract strategy class for subsequent strategies to inherit from"""

    def __init__(self):
        """Runs when strategy is instantiated, should contain initialization of needed variables, etc"""

    def on_data(self):
        """Method in strategy which will run on every new candle"""
