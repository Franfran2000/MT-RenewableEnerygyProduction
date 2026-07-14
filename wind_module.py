"""
Module for Wind power forecast
"""

from RenewModule import RenewModule

from windpowerlib import ModelChain, WindTurbine
from windpowerlib import WindFarm
from windpowerlib import WindTurbineCluster
from windpowerlib import TurbineClusterModelChain

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class WindModule(RenewModule):
    
    def __init__(self):
        super().__init__()
        self.mc = None

    def read_params(self, turbines):
        if turbines["farm"]:
            self.read_wind_farm(turbines)
        else:
            self.read_single_turbine(turbines)
    
    def read_single_turbine(self, turbine):
        wind_turbine = WindTurbine(**turbine["turbines"])
        self.mc = ModelChain(wind_turbine, **turbine["modelchain_params"])
        
    def read_wind_farm(self, turbines):
        
        wind_turbines = []
        number_of_turbines = []
        total_capacity = []
        for turbine in turbines["turbines"]:
            wind_turbine = WindTurbine(**turbine["turbine_data"])
            num_of_turbine = turbine["number_of_turbines"]
            capacity = wind_turbine.nominal_power*num_of_turbine
            
            wind_turbines.append(wind_turbine)
            number_of_turbines.append(num_of_turbine)
            total_capacity.append(capacity)
            
        wind_turbine_fleet = pd.DataFrame({
            "wind_turbine": wind_turbines,  # as windpowerlib.WindTurbine
            "number_of_turbines": number_of_turbines,
            "total_capacity": total_capacity,
        })
        
        wind_farm = WindFarm(
            name="example_farm", wind_turbine_fleet=wind_turbine_fleet, efficiency=turbines["efficiency"]
        )
        self.mc = TurbineClusterModelChain(wind_farm, **turbines["modelchain_params"])
        
    def calculate_power(self, weather):
        self.mc = self.mc.run_model(weather)
        self.power = self.mc.power_output