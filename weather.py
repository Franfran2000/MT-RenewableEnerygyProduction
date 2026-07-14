"""
Module for getting the weather forecast
"""

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

#TODO add number of days and time resolution as params
def get_wind_weather(location):
    """
    get Open Meteo forecast for wind module, by default it is set to Louvain-la-Neuve in Belgium

    Parameters
    ----------
    location: dict
        latitude: float
        longitude: float
        timezone: string
    
    Returns
    -------
    weather
        pandas dataframe containing the weather info in the correct format for the wind module
        wind speed at heights 80, 120, and 180m: {m/s}
        temperature at heights 2, 80, 120, and 180m: degree {K}
        surface air pressure: {Pa}
    """
    
    #TODO Add check for parameters
    latitude = location["latitude"]
    longitude = location["longitude"]
    timezone = location["timezone"]
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    	"latitude": latitude,
    	"longitude": longitude,
    	"hourly": ["wind_speed_80m", "wind_speed_10m", "wind_speed_120m", "temperature_80m", "temperature_120m", "temperature_2m", "wind_speed_180m", "temperature_180m", "surface_pressure"],
    	"timezone": timezone,
    	"wind_speed_unit": "ms",
    }
    responses = openmeteo.weather_api(url, params=params)
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
    abs_zero = 273.15 # Offset between degrees Celsius and Kelvin 
    
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_wind_speed_80m = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_120m = hourly.Variables(2).ValuesAsNumpy()
    hourly_temperature_80m = hourly.Variables(3).ValuesAsNumpy() + abs_zero
    hourly_temperature_120m = hourly.Variables(4).ValuesAsNumpy() + abs_zero
    hourly_temperature_2m = hourly.Variables(5).ValuesAsNumpy() + abs_zero
    hourly_wind_speed_180m = hourly.Variables(6).ValuesAsNumpy()
    hourly_temperature_180m = hourly.Variables(7).ValuesAsNumpy() + abs_zero
    hourly_surface_pressure = hourly.Variables(8).ValuesAsNumpy()
    
    
    date_index = pd.date_range(
    	start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    	end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = hourly.Interval()),
    	inclusive = "left"
    )
    hourly_data = { 
        "wind_speed": {}, 
        "temperature": {}, 
        "pressure": {}
        , "roughness_length": {"0": None}
        }
    
    hourly_data["wind_speed"]["80"]= hourly_wind_speed_80m
    hourly_data["wind_speed"]["10"] = hourly_wind_speed_10m
    hourly_data["wind_speed"]["120"] = hourly_wind_speed_120m
    hourly_data["temperature"]["80"] = hourly_temperature_80m
    hourly_data["temperature"]["120"] = hourly_temperature_120m
    hourly_data["temperature"]["2"] = hourly_temperature_2m
    hourly_data["wind_speed"]["180"] = hourly_wind_speed_180m
    hourly_data["temperature"]["180"] = hourly_temperature_180m
    hourly_data["pressure"]["0"] = hourly_surface_pressure*100 #from hPa to Pa
        
    col_tuples = [(i,j) for i in hourly_data.keys() for j in hourly_data[i].keys()]
    col_index = pd.MultiIndex.from_tuples(col_tuples)
    
    weather = pd.DataFrame(index=date_index, columns=col_index)
        
    for i, j in col_tuples:
        weather[i, j] = hourly_data[i][j]
    
    weather["roughness_length"] = 0.10  # None because it will be using hellman wind speed model
                                        # looking at source code for how it works, if we want to use default value of 1/7,
                                        # best way is to set hellman_exponent to 1/7, instead of trying to have roughness_length=None
                                        # which corresponds to around 0.10 for z0
    #TODO Change the way we manage roughness length
    return weather

def get_pv_weather(location):
    
    """
    get Open Meteo forecast for photovoltaic module

    Parameters
    ----------
    location: dict
        latitude: float
        longitude: float
        timezone: string
    
    Returns
    -------
    weather
        pandas dataframe containing the weather info in the correct format for the pv module:
            air temperature at height 2m: degree {C}
            wind speed at height 10m: {m/s}
            surface air pressure: {Pa}
            diffuse solar radiation DHI: {W/m^2}
            direct normal irradiance DNI: {W/m^2}
            shortwave solar radiation GHI: {W/m^2}
    """
    
    #TODO Add check for parameters
    latitude = location["latitude"]
    longitude = location["longitude"]
    timezone = location["tz"]
    
    #%%
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    	"latitude": latitude,
    	"longitude": longitude,
    	"hourly": ["temperature_2m", "wind_speed_10m", "surface_pressure", "diffuse_radiation", "direct_normal_irradiance", "shortwave_radiation"],
    	"timezone": timezone,
        "wind_speed_unit": "ms",
    }
    responses = openmeteo.weather_api(url, params=params)
    
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
    
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
    
    hourly_data["temp_air"] = hourly_temperature_2m
    hourly_data["wind_speed"] = hourly_wind_speed_10m
    hourly_data["surface_pressure"] = hourly_surface_pressure*100 #from hPa to Pa
    hourly_data["dhi"] = hourly_diffuse_radiation
    hourly_data["dni"] = hourly_direct_normal_irradiance
    hourly_data["ghi"] = hourly_shortwave_radiation
    
    hourly_data = pd.DataFrame(data = hourly_data)
    # print("\nHourly data\n", hourly_data)
    
    #%% 
    weather = hourly_data.set_index("date")

    return weather