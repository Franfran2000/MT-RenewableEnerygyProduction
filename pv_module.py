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
        self.location = location
        self.temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    
    def read_params(self, module_name, inverter_name, surface_azimuth, temperature_model):
        #TODO allow module and inverter to be directly given as argument
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        
        self.system = {}
        
        self.system["module"] = sandia_modules[module_name]
        self.system["inverter"] = sapm_inverters[inverter_name]
        self.system["surface_azimuth"] = surface_azimuth
        
        temp_mod_name = temperature_model["name"]
        temp_mod_config = temperature_model["configuration"]
        self.temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[temp_mod_name][temp_mod_config]    
        
        
    def calculate_power(self, weather):
        module = self.system["module"]
        inverter = self.system["inverter"]
        
        latitude, longitude, name, altitude, timezone = self.location
        location = Location(
            latitude,
            longitude,
            name=name,
            altitude=altitude,
            tz=timezone,
        )
        mount = FixedMount(surface_tilt=latitude, surface_azimuth=180)
        array = Array(
            mount=mount,
            module_parameters=module,
            temperature_model_parameters=self.temperature_model_parameters,
        )
        system = PVSystem(arrays=[array], inverter_parameters=inverter)
        mc = ModelChain(system, location)
        mc.run_model(weather)
        self.power = mc.results.ac
        print(self.power)
        return 1