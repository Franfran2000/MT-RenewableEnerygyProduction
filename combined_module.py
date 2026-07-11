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
    
    # Infrastructure information
    location = { 
        "pv": {
            "latitude": 50.67,
            "longitude": 4.62,
            "name": "Louvain-la-Neuve",
            "altitude": 123,
            "timezone": "Europe/Berlin",
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
    # ------------------------------------------------------------------
    # PV installation
    # ------------------------------------------------------------------

    pv = PVModule(location)
    pv.read_params(
        module_name="Canadian_Solar_CS5P_220M___2009_",
        inverter_name="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
        number_of_modules=20,
        surface_tilt=35,
        surface_azimuth=180,
    )
    pv.calculate_power(pv_weather)
    pv_power = pv.get_power()
    print(pv_power)
    # ------------------------------------------------------------------
    # Wind installation
    # ------------------------------------------------------------------

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