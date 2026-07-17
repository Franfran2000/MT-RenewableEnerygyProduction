# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 16:09:14 2026

@author: Francis Jacobs
"""

import pvlib

import pandas as pd

import matplotlib.pyplot as plt


coordinates = [
    (32.2, -111.0, 'Tucson', 700, 'Etc/GMT+7'),
    (35.1, -106.6, 'Albuquerque', 1500, 'Etc/GMT+7'),
    (37.8, -122.4, 'San Francisco', 10, 'Etc/GMT+8'),
    (52.5, 13.4, 'Berlin', 34, 'Etc/GMT-1'),
]


sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

tmys = []

for location in coordinates:
    latitude, longitude, name, altitude, timezone = location
    weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude)[0]
    weather.index.name = "utc_time"
    tmys.append(weather)

from pvlib.pvsystem import PVSystem, Array, FixedMount, SingleAxisTrackerMount

from pvlib.location import Location

from pvlib.modelchain import ModelChain

energies = {}

for location, weather in zip(coordinates, tmys):
    latitude, longitude, name, altitude, timezone = location
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
        temperature_model_parameters=temperature_model_parameters,
    )
    system = PVSystem(arrays=[array], inverter_parameters=inverter)
    mc = ModelChain(system, location)
    mc.run_model(weather)
    annual_energy = mc.results.ac.sum()
    energies[name] = annual_energy


energies = pd.Series(energies)


print(energies)


def calculate_power(self, weather):
    
    latitude, longitude, name, altitude, timezone = self.location

    self.system['surface_tilt'] = latitude
    
    solpos = pvlib.solarposition.get_solarposition(
    
        time=weather.index,
    
        latitude=latitude,
    
        longitude=longitude,
    
        altitude=altitude,
    
        temperature=weather["temperature_2m"],
    
        pressure=weather["surface_pressure"],
    
    )
    
    dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
    
    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    
    pressure = pvlib.atmosphere.alt2pres(altitude)
    
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    
    aoi = pvlib.irradiance.aoi(
    
        self.system['surface_tilt'],
    
        self.system['surface_azimuth'],
    
        solpos["apparent_zenith"],
    
        solpos["azimuth"],
    
    )
    
    total_irradiance = pvlib.irradiance.get_total_irradiance(
    
        self.system['surface_tilt'],
    
        self.system['surface_azimuth'],
    
        solpos['apparent_zenith'],
    
        solpos['azimuth'],
    
        weather['direct_normal_irradiance'],
    
        weather['shortwave_radiation'],
    
        weather['diffuse_radiation'],
    
        dni_extra=dni_extra,
    
        model='haydavies',
    
    )
    
    cell_temperature = pvlib.temperature.sapm_cell(
    
        total_irradiance['poa_global'],
    
        weather["temperature_2m"],
    
        weather["wind_speed_10m"],
    
        **self.temperature_model_parameters,
    
    )
    
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
    
        total_irradiance['poa_direct'],
    
        total_irradiance['poa_diffuse'],
    
        am_abs,
    
        aoi,
    
        self.system["module"],
    
    )
    
    dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, self.system["module"])
    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], self.system["inverter"])
    
    self.power = ac
    
    return 1



energies.plot(kind='bar', rot=0)


plt.ylabel('Yearly energy yield (W hr)')