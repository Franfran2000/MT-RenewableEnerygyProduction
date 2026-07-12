"""
Renewable Energy Production
"""

import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np

import weather as wt
from pv_module import PVModule
from wind_module import WindModule

def main():
    #TODO read the inputs from json files
    #TODO create file similar to weather that manages IO for each module
    
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
            "module": "Panasonic_VBHN235SA06B__2013_",
            "mount": "fixed",
            "surface_tilt": 35,
            "surface_azimuth": 180,
            "modules_per_string": 2,
            "strings": 2,
            "temperature_model": ("sapm",  "open_rack_glass_glass")
        },
        {
            "module": "Canadian_Solar_CS5P_220M___2009_",
            "mount": "tracker",
            "axis_tilt": 0,
            "axis_azimuth": 180,
            "max_angle": 60,
            "backtrack": True,
            "temperature_model": ("sapm",  "open_rack_glass_glass")

        },
    ]
    pv.read_params(arrays=arrays,
                   inverter_name="ABB__MICRO_0_25_I_OUTD_US_208__208V_")
    pv.calculate_power(pv_weather)
    pv_power = pv.get_power()
    # print(pv_power)
    # pv_power.plot()
    # plt.xlabel("Time in Days")
    # plt.ylabel('Hourly power output (W)')
    # plt.show()
    
    # Wind Module
    wind = WindModule()
    wind.read_params(
        turbine_type="E-126/4200",
        hub_height=135,
        number_of_turbines=3,
    )
    wind.calculate_power(wind_weather)
    wind_power = wind.get_power()


if __name__ == "__main__":
    main()