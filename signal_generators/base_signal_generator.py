class BaseSignalGenerator:
    """Defines an abstract strategy class for subsequent signal generators to inherit from"""

    def __init__(self):
        """Runs when generator is instantiated, should contain initialization of needed variables, etc"""

    def on_data(self):
        """Will run on every new candle"""
