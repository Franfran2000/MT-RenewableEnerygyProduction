
class RenewModule():
    """
    Abstract class for renewable energy production modules
    """

    def __init__(self):
        self.power = None

    def read_params(self, *args, **kwargs):
        """
        Read the parameters describing the renewable infrastructure
        """
        pass

    def calculate_power(self, weather):
        """
        Calculate the power output from the provided weather data

        Parameters
        ----------
        weather : pandas.DataFrame
            Weather data required by the specific renewable technology

        Returns
        -------
        pandas.Series
            Power output
        """
        pass

    def get_power(self):
        """
        Returns calculated power output
        """
        return self.power