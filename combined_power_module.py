"""
Total Renewable Energy Production
"""

import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np

import weather as wt
from pv_module import PVModule
from wind_module import WindModule

def renewable_powers(configurations):
    """
    Computes the power forecast for each renewable module, based on the configurations

    Parameters
    ----------
    configurations : list of dicts
        configuration info for each module

    Returns
    -------
    total_power : dict
        dictionary containing power forecast time series for each module
    """

    #TODO read the inputs from json files
    
    # Location information
    location = { 
        "pv": {
            "latitude": 50.67,
            "longitude": 4.62,
            "name": "Louvain-la-Neuve",
            "altitude": 123,
            "tz": "Europe/Berlin",
            },
        "wind": { 
            "latitude": 50.67,
            "longitude": 4.62,
            "timezone": "Europe/Berlin",
            }
    }
    # Weather
    pv_weather = wt.get_pv_weather(location["pv"])
    wind_weather = wt.get_wind_weather(location["wind"])
    
    # PV Module
    pv = PVModule(location["pv"])
    arrays = [
        {
            "module": "Canadian_Solar_CS5P_220M___2009_",
            "mount": {"type": "fixed", 
                      "params": {
                            "surface_tilt": 35,
                            "surface_azimuth": 180,
                            }
                      }, 
            "modules_per_string": 1,
            "strings": 1,
            "temperature_model": ("sapm",  "open_rack_glass_glass")
        },
        #     "module": "Panasonic_VBHN235SA06B__2013_",
        #     "mount": {"type" :"tracker", 
        #               "params": {
        #                     "axis_tilt": 0,
        #                     "axis_azimuth": 180,
        #                     "max_angle": 60,
        #                     "backtrack": True,
        #                     }
        #               },
        #     "modules_per_string": 1,
        #     "strings": 1,
        #     "temperature_model": ("sapm",  "open_rack_glass_glass")

        # },
        {
            "module": "Panasonic_VBHN235SA06B__2013_",
            "mount": {"type": "fixed", 
                      "params": {
                            "surface_tilt": 30,
                            "surface_azimuth": 180,
                            }
                      }, 
            "temperature_model": ("sapm",  "open_rack_glass_polymer")
        },
    ]
    pv.read_params(arrays=arrays,
                   inverter_name="iPower__SHO_5_2__240V_")
    pv.calculate_power(pv_weather)
    pv_power = pv.get_power()
    # print(pv_power)
    
    # Wind Module
    wind = WindModule()
    # turbines = {
    #     "farm": False,
    #     "turbines": {"turbine_type": "E-126/4200",  # turbine type as in register
    #                   "hub_height": 135,  # in m
    #                   },
    #     "modelchain_params": {
    #                 "wind_speed_model": "hellman",  # 'logarithmic' (default),
    #                                                 # 'hellman' or
    #                                                 # 'interpolation_extrapolation'
    #                 "density_model": "ideal_gas",   # 'barometric' (default), 'ideal_gas' or
    #                                                 # 'interpolation_extrapolation'
    #                 "temperature_model": "linear_gradient",  # 'linear_gradient' (def.) or
    #                                                           # 'interpolation_extrapolation'
    #                 "power_output_model": "power_curve",  # 'power_curve'
    #                                                       # (default) or 'power_coefficient_curve'
    #                 "density_correction": True,  # False (default) or True
    #                 "obstacle_height": 0,  # default: 0
    #                 "hellman_exp": 1/7, # None (default) or float
    #             }  
    #     }
    turbines = {
        "farm": True,
        "turbines": [{"number_of_turbines": 3, "turbine_data": {"turbine_type": "E-126/4200", "hub_height": 135}},
                     {"number_of_turbines": 2, "turbine_data": {"turbine_type":"N131/3000", "hub_height": 114}}],
        "efficiency": 0.9,
        "modelchain_params": {
            "wake_losses_model": "wind_farm_efficiency",
            # 'dena_mean' (default), None,
            # 'wind_farm_efficiency' or name
            #  of another wind efficiency curve
            #  see :py:func:`~.wake_losses.get_wind_efficiency_curve`
            "smoothing": True,  # False (default) or True
            "block_width": 0.5,  # default: 0.5
            "standard_deviation_method": "Staffell_Pfenninger",  #
            # 'turbulence_intensity' (default)
            # or 'Staffell_Pfenninger'
            "smoothing_order": "wind_farm_power_curves",  #
            # 'wind_farm_power_curves' (default) or
            # 'turbine_power_curves'
            "wind_speed_model": "logarithmic",
            # 'logarithmic' (default), 'hellman' or 'interpolation_extrapolation'
            "density_model": "ideal_gas",  #
            # 'barometric' (default), 'ideal_gas' or 'interpolation_extrapolation'
            "temperature_model": "linear_gradient",
            # 'linear_gradient' (def.) or 'interpolation_extrapolation'
            "power_output_model": "power_curve",
            # 'power_curve' (default) or 'power_coefficient_curve'
            "density_correction": True,  # False (default) or True
            "obstacle_height": 0,  # default: 0
            "hellman_exp": 1/7,
            }  # None (default) or None
        }


    wind.read_params(turbines)
    wind.calculate_power(wind_weather)
    wind_power = wind.get_power()
    
    total_power = {"pv": pv_power, "wind": wind_power}
    
    return total_power
    
    # # print(wind_power)
    # pv_power.plot()
    # plt.xlabel("Date")
    # plt.ylabel('Hourly PV power output (W)')
    # plt.show()
    
    # wind_power.plot()
    # plt.xlabel("Date")
    # plt.ylabel('Hourly Wind power output (W)')
    # plt.show()
        
    # total_power = pv_power + wind_power/1e4
    # total_power.plot()
    # plt.xlabel("Date")
    # plt.ylabel('Hourly total power output (W)')
    # plt.show()
    
if __name__ == "__main__":
    renewable_powers()