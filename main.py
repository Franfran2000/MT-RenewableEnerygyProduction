"""
Main module
Input paths to config json, and consumption data
"""

from matplotlib import pyplot as plt
from power_module import renewable_powers
import json

def main(configuration_files_paths, consumption=None):
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
    
    # parse configurations
    # define parse function
    # define configuration example json, make it easy to understand
    configs = []
    for configfile in configuration_files_paths:
        configuration = parse_configfile(configfile)
        configs.append(configuration)
    
    # call power compute module
    powers = []
    for cfg in configs:
        powers.append(renewable_powers(cfg)) # each element is a list of modules with their calculated power
    
    # compute auto-consumption
    # need to pre-process datasets
    
    # compare configurations and compare auto-consumptions
    # give terminal line info: how many percents difference there are, etc

    # plots
    for config_power in powers:
        for config_type, config_modules in config_power.items():
            power = config_modules[0].get_power()
            for power_mod in config_modules[1:]:
                power += power_mod.get_power()

            config_type = config_type[:-len("_modules")]
            power.plot()
            plt.xlabel("Date")
            plt.ylabel(f"{config_type} power output (W)")
            plt.show()


def parse_configfile(configfile):
    with open(configfile, "r") as cfg:
        config = json.load(cfg)
    return config

main(["pv.json", "wind.json"])