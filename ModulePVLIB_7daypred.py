"""
Module for predicting power output of renewable energy sources
"""
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# latitude, longitude, name, altitude, timezone
location = (50.67, 4.62, 'Louvain-la-Neuve', 123, 'Etc/GMT+2')


# get the module and inverter specifications from SAM

sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

#%%
def getOpenMeteoWeather(lat=50.6683, long=4.6144, timez="Europe/Berlin"):
    import openmeteo_requests
    
    import requests_cache
    from retry_requests import retry
    #%%
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    	"latitude": lat,
    	"longitude": long,
    	"hourly": ["temperature_2m", "wind_speed_10m", "surface_pressure", "diffuse_radiation", "direct_normal_irradiance", "shortwave_radiation"],
    	"timezone": timez,
        "wind_speed_unit": "ms",
    }
    responses = openmeteo.weather_api(url, params=params)
    
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
    
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(1).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(2).ValuesAsNumpy()
    hourly_diffuse_radiation = hourly.Variables(3).ValuesAsNumpy()
    hourly_direct_normal_irradiance = hourly.Variables(4).ValuesAsNumpy()
    hourly_shortwave_radiation = hourly.Variables(5).ValuesAsNumpy()
    
    hourly_data = {"date": pd.date_range(
    	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )}
    
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["surface_pressure"] = hourly_surface_pressure*100 #from hPa to Pa
    hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
    hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
    
    hourly_data = pd.DataFrame(data = hourly_data)
    print("\nHourly data\n", hourly_data)
    
    #%% 
    weather = hourly_data.set_index("date")
    print(weather.index)
    print(weather["temperature_2m"])
    print(weather["wind_speed_10m"])
    print(weather["surface_pressure"])
    print(weather["diffuse_radiation"])
    print(weather["direct_normal_irradiance"])
    print(weather["shortwave_radiation"])
    return weather

#%%
weather = getOpenMeteoWeather()
print(weather)


#%%
def getACPower():
    system = {'module': module, 'inverter': inverter,
    
              'surface_azimuth': 180}
    
    latitude, longitude, name, altitude, timezone = location
    
    system['surface_tilt'] = latitude
    
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
    return ac


def run_example():
    ac = getACPower()
    print(ac)
    # plt.plot(np.arange(len(ac)), ac)
    ac.plot()
    plt.xlabel("Time in Days")
    plt.ylabel('Hourly power output (W)')
    
    plt.show()

#%%
