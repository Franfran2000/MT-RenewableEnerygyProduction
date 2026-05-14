"""
Module for predicting power output of renewable energy sources
"""
import pvlib
import pandas as pd
import matplotlib.pyplot as plt

# latitude, longitude, name, altitude, timezone
coordinates = [
    (50.67, 4.62, 'Louvain-la-Neuve', 123, 'Etc/GMT+2')
]
print(coordinates)

# get the module and inverter specifications from SAM

sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

tmys = [] #Typical meteorological year

for location in coordinates:

    latitude, longitude, name, altitude, timezone = location

    weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude)[0] #Data from PVGIS

    weather.index.name = "utc_time"

    tmys.append(weather)
#%%
print(tmys[0].index)
#%% 
system = {'module': module, 'inverter': inverter,

          'surface_azimuth': 180}


energies = {}

for location, weather in zip(coordinates, tmys):
    
    print(weather["T2m"])
    print(weather["SP"])
    print(weather['Gb(n)'])
    print(weather['G(h)'])
    print(weather['Gd(h)'])
    print(weather["WS10m"])
#%%
    latitude, longitude, name, altitude, timezone = location

    system['surface_tilt'] = latitude

    solpos = pvlib.solarposition.get_solarposition(

        time=weather.index,

        latitude=latitude,

        longitude=longitude,

        altitude=altitude,

        temperature=weather["T2m"],

        pressure=weather["SP"],

    )

    dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)

    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])

    pressure = pvlib.atmosphere.alt2pres(altitude)

    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

    aoi = pvlib.irradiance.aoi(

        system['surface_tilt'],

        system['surface_azimuth'],

        solpos["apparent_zenith"],

        solpos["azimuth"],

    )

    total_irradiance = pvlib.irradiance.get_total_irradiance(

        system['surface_tilt'],

        system['surface_azimuth'],

        solpos['apparent_zenith'],

        solpos['azimuth'],

        weather['Gb(n)'],

        weather['G(h)'],

        weather['Gd(h)'],

        dni_extra=dni_extra,

        model='haydavies',

    )

    cell_temperature = pvlib.temperature.sapm_cell(

        total_irradiance['poa_global'],

        weather["T2m"],

        weather["WS10m"],

        **temperature_model_parameters,

    )

    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(

        total_irradiance['poa_direct'],

        total_irradiance['poa_diffuse'],

        am_abs,

        aoi,

        module,

    )

    dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, module)

    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)
    print(sorted(ac))
    annual_energy = ac.sum()

    energies[name] = annual_energy



energies = pd.Series(energies)

# based on the parameters specified above, these are in W*hrs

# print(energies)

energies.plot(kind='bar', rot=0)
plt.ylabel('Yearly energy yield (W hr)')

plt.show()