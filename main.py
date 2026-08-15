"""
Main module
Input paths to config json, and consumption data
"""

from matplotlib import pyplot as plt
from power_module import renewable_powers
import pandas as pd
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
    
    Returns
    ----------
    results : dictionary of results
    configurations are the simulation results for each installation
    comparisons are the results of comparisons of each installation against each other
    self_consumption are the results for how much of generated power is consumed by the local network
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
    
    # plots
    for config_power in powers:
        for config_type, config_modules in config_power.items():
            power = config_modules[0].get_power()
            for power_module in config_modules[1:]:
                power += power_module.get_power()
            
            config_type = config_type[:-len("_modules")]
            power.plot()
            plt.title(f"Daily {config_type} power output")
            plt.xlabel("Date")
            plt.ylabel(f"{config_type} power output (W)")
            plt.show()
            
            energy = power.sum()*0.25/1000 # [kWh] 15 minute interval, not whole hour
            print("Simulated total energy output", energy, "kWh")
    
    # compare configurations to the others
    comparisons = compare_configs(powers)
    
    # prepare results return dictionary
    results = {"configurations": powers,
               "comparisons": comparisons}
    
    # if there is consumption data, compute it and return it
    if consumption is not None:
        self_consumption = calculate_self_consumption(powers, consumption)
        results["self_consumption"] = self_consumption
    
    return results
    
def compare_configs(powers):
    
    return

def parse_configfile(configfile):
    with open(configfile, "r") as cfg:
        config = json.load(cfg)
    return config

def calculate_self_consumption(powers, consumption):
        for config_power in powers:
            for config_type, config_modules in config_power.items():
                power = config_modules[0].get_power()
                for power_module in config_modules[1:]:
                    power += power_module.get_power()
    
        consumption = consumption.sum(axis=1) # here we lose who consumed what #TODO would be good to remember who consumes or not to give better recommendations
        consumption.index = power.index # patchwork because consumption data does not have Daylight Savings time changes, resulting in misaligned indices while keeping the same amount of total data points
                                        # October has a longer day and March has a shorter day that cancels out
        consumption.plot()
        plt.title("Daily power usage")
        plt.xlabel("Date")
        plt.ylabel("Total power consumption (W)")
        plt.show()

        self_cons = pd.DataFrame({
            "consumption": consumption,
            "power": power
        }).min(axis=1)
        
        self_cons[self_cons < 0] = 0
        
        self_cons.plot()
        plt.title("Daily self consumption")
        plt.xlabel("Date")
        plt.ylabel("Self consumption (W)")
        plt.show()
        
        injection = power - self_cons
        
        injection.plot()
        plt.title("Daily injection")
        plt.xlabel("Date")
        plt.ylabel("Daily injection (W)")
        plt.show()
        
        print("total actual consumed energy", consumption.sum()*0.25/1000, "kWh")
        print("Total self-consumption", self_cons.sum()*0.25/1000, "kWh")
        print("Total injection", injection.sum()*0.25/1000, "kWh")

        return self_cons