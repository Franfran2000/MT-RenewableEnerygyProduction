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
        """
        Parameters
        ----------
        location : dict
            latitude, longitude, altitude, timezone and name of the location
        """
        super().__init__() 
        self.location = Location(**location)
        self.installations_mc = [] # list of modelchains
        
    def read_params(self, systems):
        """
        #TODO Change description
        #TODO separate into multiple subfunctions
        Reads the input defining a PV system of arrays of pv modules connected to a single inverter
        The description of these variables is taken from the pvlib documentation

        Parameters
        ----------
        arrays : list of dict
            each dictionary defines one array, for each array is provided:
                mount type: string
                    fixed or single axis tracker 
                    
                    Fixed mount params:
                    surface_tilt : float, default 0
                        Surface tilt angle. The tilt angle is defined as angle from horizontal
                        (e.g. surface facing up = 0, surface facing horizon = 90) [degrees]

                    surface_azimuth : float, default 180
                        Azimuth angle of the module surface. North=0, East=90, South=180,
                        West=270. [degrees]

                    
                    SingleAxisTracker mount params:
                    axis_tilt : float, default 0
                        The tilt of the axis of rotation (i.e, the y-axis defined by
                        axis_azimuth) with respect to horizontal. [degrees]

                    axis_azimuth : float, default 180
                        A value denoting the compass direction along which the axis of
                        rotation lies, measured east of north. [degrees]

                    max_angle : float, default 90
                        A value denoting the maximum rotation angle
                        of the one-axis tracker from its horizontal position (horizontal
                        if axis_tilt = 0). A max_angle of 90 degrees allows the tracker
                        to rotate to a vertical position to point the panel towards a
                        horizon. max_angle of 180 degrees allows for full rotation. [degrees]

                    backtrack : bool, default True
                        Controls whether the tracker has the capability to "backtrack"
                        to avoid row-to-row shading. False denotes no backtrack
                        capability. True denotes backtrack capability.

                    gcr : float, default 2.0/7.0
                        A value denoting the ground coverage ratio of a tracker system
                        which utilizes backtracking; i.e. the ratio between the PV array
                        surface area to total ground area. A tracker system with modules
                        2 meters wide, centered on the tracking axis, with 6 meters
                        between the tracking axes has a gcr of 2/6=0.333. If gcr is not
                        provided, a gcr of 2/7 is default. gcr must be <=1. [unitless]

                    cross_axis_tilt : float, default 0.0
                        The angle, relative to horizontal, of the line formed by the
                        intersection between the slope containing the tracker axes and a plane
                        perpendicular to the tracker axes. Cross-axis tilt should be specified
                        using a right-handed convention. For example, trackers with axis
                        azimuth of 180 degrees (heading south) will have a negative cross-axis
                        tilt if the tracker axes plane slopes down to the east and positive
                        cross-axis tilt if the tracker axes plane slopes up to the east. Use
                        :func:`~pvlib.tracking.calc_cross_axis_tilt` to calculate
                        `cross_axis_tilt`. [degrees]
    
                
                #TODO make it possible to pass custom module parameters ?
                module name: string
                    name of the solar pv module composing the array to look up in the SAPM database
               
                modules per string: int, default 1
                    Number of modules per string in the array
                
                strings: int, default 1
                    Number of parallel strings in the array
                
                temperature model: tuple of strings
                    first string defines which model from SAPM or PVSyst is used
                    second string defines which configuration for the model is used

                
        #TODO make it possible to pass custom inverter parameters ?    
        inverter_name : string
            name of the inverter to look up in the SAPM database
        
        """
        #TODO allow list of inverter names, and have arrays be a list of list of dicts
        #One PVSyst and one ModelChain per inverter, so if multiple inverters then we need to add up all the multiple powers
        
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        
        for system in systems:
            
            inverter = sapm_inverters[system["inverter_name"]]
            arrays = []
            for config in system["arrays"]:
                
                module = sandia_modules[config["module"]]
                
                temp_mod_name, temp_mod_config = config["temperature_model"]
                temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[temp_mod_name][temp_mod_config]    
                
                mount = None
                if config["mount"]["type"] == "fixed":
                    params = config["mount"]["params"]
                    mount = FixedMount(**params)
    
                elif config["mount"]["type"] == "tracker":
                    params = config["mount"]["params"]
                    mount = SingleAxisTrackerMount(**params)
                else:
                    raise ValueError(f"Unknown mount type: {config['mount']}")
                
                array = Array(mount=mount,
                              module_parameters=module,
                              temperature_model_parameters=temperature_model_parameters,
                              modules_per_string=config.get("modules_per_string", 1),
                              strings=config.get("strings", 1))
    
                arrays.append(array)
    
            pvsystem = PVSystem(arrays=self.arrays, inverter_parameters=inverter)
            mc = ModelChain(pvsystem, self.location)
            
            self.installations_mc.append(mc)
        
    def calculate_power(self, weather):
        install_powers = []
        for install_mc in self.installations_mc:
            install_mc.run_model(weather)
            install_power = install_mc.results.ac
            install_powers.append(install_power)
            
        self.power = pd.concat(install_powers, axis=1).sum(axis=1) #aggregated sum of all pv installations at a single location
        