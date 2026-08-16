"""
Total Renewable Energy Production
"""

import weather as wt
from pv_module import PVModule
from wind_module import WindModule

def renewable_powers(configs):
    """
    Computes the power forecast for each renewable module, based on the configuration

    Parameters
    ----------
    configs : list of dicts
        configuration info for each module

    Returns
    -------
    total_power : dict
        dictionary containing power forecast time series for each module
    """
    
    modules = {}
    
    # Init list for each module type
    pv_modules = []
    wind_modules = []
    
    weather_params = configs["weather"]

    for cfg in configs["configs"]:
        cfg_type = cfg["type"]
                
        if cfg_type == "pv":
            # multiple different locations possible
            pv_installations = cfg["installations"]
            for pv_install in pv_installations:
                pv_location = pv_install["location"]
                pv_weather = wt.get_pv_weather(pv_location, weather_params)
                
                # one module per location, multiple systems (each linked to one inverter) per module
                pv_systems = pv_install["systems"]
                pv = PVModule(pv_location)
                pv.read_params(pv_systems)
                pv.calculate_power(pv_weather)
            
                pv_modules.append(pv) # append PVModule object directly
                
        elif cfg_type == "wind": 
            # one call per location
            wind_installations = cfg["installations"]
            for wind_install in wind_installations: 
                wind_location = wind_install["location"]
                wind_weather = wt.get_wind_weather(wind_location, weather_params)
                
                wind = WindModule()
                wind.read_params(wind_install["turbines"])
                wind.calculate_power(wind_weather)
                
                wind_modules.append(wind)
    
    if pv_modules:
        modules["pv_modules"] = pv_modules
    if wind_modules:
        modules["wind_modules"] = wind_modules
    
    return modules
