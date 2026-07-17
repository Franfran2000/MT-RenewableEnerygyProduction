"""
Main module
Input paths to config json, and consumption data
"""

from combined_power_module import renewable_powers
import json

def main(configuration_files, consumption=None):
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
    #define configuration example json, make it easy to understand
    configs = []
    for configfile in configuration_files:
        configuration = parse_configfile(configuration_files)
        configs.append(configuration)
    
    #call power compute module
    powers = []
    for cfg in configs:
        powers.append(renewable_powers(cfg)) #each element is a list of modules with their calculated power
    #plot and compare each power forecast

    # compute auto-consumption
    # might need to modify both datasets to fit them
    
    #compare configurations and compare auto-consumptions
    #give terminal line info: how many percents difference there are, etc
    

def parse_configfile(configfile):
    with open(configfile), "r" as cfg:
        config = json.load(cfg)
    return config
