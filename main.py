"""
Main module
Input paths to config json, and consumption data
"""

from combined_power_module import renewable_powers


def main(configurations, consumption=None):
    """
    Simulate or compare different renewable configurations with each other
    Compute auto-consumption of power if consumption data is provided
        
    Parameters
    ----------
    configurations : list of strings
        paths to the json files containing each configuration to be compared with one another
    consumption : string, optional
        path to consumption data used to compute auto-consumption

    """
    
    #parse configurations
    #define parse function
    #defne configuration example json, make it easy to understand
    
    
    #call combined power module
    #plot and compare each power forecast
    
    #compute auto-consumption
    #   might need to modify both datasets to fit them
    
    #compare configurations and compare auto-consumptions
    #give terminal line info: how many percents difference there are, etc
    