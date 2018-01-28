class BaseSignalGenerator:
    """Defines an abstract strategy class for subsequent signal generators to inherit from"""

    def __init__(self):
        """Runs when generator is instantiated, should contain initialization of needed variables, etc"""

    def check_condition(self, new_candle):
        """Should run on every new candle"""
