"""
Module for Photovoltaic (PV) power forecast
"""
from RenewModule import RenewModule

import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pvlib.pvsystem import PVSystem, Array, FixedMount, SingleAxisTrackerMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain


class PVModule(RenewModule):
    
    def __init__(self, location):
        super().__init__() 
        self.location = Location(**location)

    def read_params(self, module_names, inverter_names, surface_azimuth, temperature_models):
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        
        self.module = sandia_modules[module_names]
        self.inverter = sapm_inverters[inverter_names]
        self.surface_azimuth = surface_azimuth
        
        temp_mod_name = temperature_models[0]
        temp_mod_config = temperature_models[1]
        self.temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[temp_mod_name][temp_mod_config]    
        
                        
        mount = FixedMount(surface_tilt=self.location.latitude, surface_azimuth=180)
        array = Array(
            mount=mount,
            module_parameters=self.module,
            temperature_model_parameters=self.temperature_model_parameters,
        )
        pvsystem = PVSystem(arrays=[array], inverter_parameters=self.inverter)
        self.mc = ModelChain(pvsystem, self.location)
        
    def calculate_power(self, weather):
        self.mc.run_model(weather)
        self.power = self.mc.results.ac
        