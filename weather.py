"""
Module for getting the weather forecast
"""

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

#TODO add number of days and time resolution as params
def get_wind_weather(location, weather_params):
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
   
    wind_weather_variables = ["wind_speed_80m", "wind_speed_10m", "wind_speed_120m", "temperature_80m", "temperature_120m", "temperature_2m", "wind_speed_180m", "temperature_180m", "surface_pressure"]
    response_data, timezone_param = get_weather(location, weather_params, wind_weather_variables)
    
    abs_zero = 273.15 # Offset between degrees Celsius and Kelvin 
    data_wind_speed_80m = response_data.Variables(0).ValuesAsNumpy()
    data_wind_speed_10m = response_data.Variables(1).ValuesAsNumpy()
    data_wind_speed_120m = response_data.Variables(2).ValuesAsNumpy()
    data_temperature_80m = response_data.Variables(3).ValuesAsNumpy() + abs_zero
    data_temperature_120m = response_data.Variables(4).ValuesAsNumpy() + abs_zero
    data_temperature_2m = response_data.Variables(5).ValuesAsNumpy() + abs_zero
    data_wind_speed_180m = response_data.Variables(6).ValuesAsNumpy()
    data_temperature_180m = response_data.Variables(7).ValuesAsNumpy() + abs_zero
    data_surface_pressure = response_data.Variables(8).ValuesAsNumpy()
    
    date_index = pd.date_range(
		start = pd.to_datetime(response_data.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(response_data.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = response_data.Interval()),
		inclusive = "left"
	).tz_convert(timezone_param)
    response_dict = { 
        "wind_speed": {}, 
        "temperature": {}, 
        "pressure": {}
        , "roughness_length": {"0": None}
        }
    
    response_dict["wind_speed"]["80"]= data_wind_speed_80m
    response_dict["wind_speed"]["10"] = data_wind_speed_10m
    response_dict["wind_speed"]["120"] = data_wind_speed_120m
    response_dict["temperature"]["80"] = data_temperature_80m
    response_dict["temperature"]["120"] = data_temperature_120m
    response_dict["temperature"]["2"] = data_temperature_2m
    response_dict["wind_speed"]["180"] = data_wind_speed_180m
    response_dict["temperature"]["180"] = data_temperature_180m
    response_dict["pressure"]["0"] = data_surface_pressure*100 #from hPa to Pa
        
    col_tuples = [(i,j) for i in response_dict.keys() for j in response_dict[i].keys()]
    col_index = pd.MultiIndex.from_tuples(col_tuples)
    
    weather = pd.DataFrame(index=date_index, columns=col_index)
        
    for i, j in col_tuples:
        weather[i, j] = response_dict[i][j]
    
    weather["roughness_length"] = 0.10  # None because it will be using hellman wind speed model
                                        # looking at source code for how it works, if we want to use default value of 1/7,
                                        # best way is to set hellman_exponent to 1/7, instead of trying to have roughness_length=None
                                        # which corresponds to around 0.10 for z0
    #TODO Change the way we manage roughness length
    return weather

def get_pv_weather(location, weather_params):
    
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
            diffuse solar radiation DHI: {W/m^2}
            direct normal irradiance DNI: {W/m^2}
            shortwave solar radiation GHI: {W/m^2}
    """
    
    
    solar_weather_variables = ["temperature_2m", "wind_speed_10m", "diffuse_radiation", "direct_normal_irradiance", "shortwave_radiation"]
    response_data, timezone_param = get_weather(location, weather_params, solar_weather_variables)
    
    response_data_temperature_2m = response_data.Variables(0).ValuesAsNumpy()
    response_data_wind_speed_10m = response_data.Variables(1).ValuesAsNumpy()
    response_data_diffuse_radiation = response_data.Variables(2).ValuesAsNumpy()
    response_data_direct_normal_irradiance = response_data.Variables(3).ValuesAsNumpy()
    response_data_shortwave_radiation = response_data.Variables(4).ValuesAsNumpy()
    
    response_dict = {"date": pd.date_range(
    	start = pd.to_datetime(response_data.Time(), unit = "s", utc = True),
    	end =  pd.to_datetime(response_data.TimeEnd(), unit = "s", utc = True),
    	freq = pd.Timedelta(seconds = response_data.Interval()),
    	inclusive = "left"
        ).tz_convert(timezone_param)
    }
    
    response_dict["temp_air"] = response_data_temperature_2m
    response_dict["wind_speed"] = response_data_wind_speed_10m
    response_dict["dhi"] = response_data_diffuse_radiation
    response_dict["dni"] = response_data_direct_normal_irradiance
    response_dict["ghi"] = response_data_shortwave_radiation
    
    response_dataframe = pd.DataFrame(data = response_dict)
    
    #%% 
    weather = response_dataframe.set_index("date")

    return weather


def get_weather(location, weather_params, weather_variables):
    """
    get Open Meteo forecast for specified weather variables

    Parameters
    ----------
    location: dict
        latitude: float
        longitude: float
        timezone: string
    Returns
    -------
    response_data
    timezone_param
    """
    
    #TODO Add check for parameters
    latitude = location["latitude"]
    longitude = location["longitude"]
    timezone = location["tz"]
    
    start_date = weather_params["start_date"]
    end_date = weather_params["end_date"]
    forecast_reso = weather_params["forecast_reso"]
    
    historical = False
    if start_date and end_date:
        historical = True
    
    #%%
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    # default behaviour is seven day forecast
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
    	"latitude": latitude,
    	"longitude": longitude,
    	forecast_reso: weather_variables,
    	"timezone": timezone,
        "wind_speed_unit": "ms",
    }
    
    if "past_days" in weather_params:
        params["past_days"] = weather_params["past_days"]
    
    if "forecast_days" in weather_params:
        params["forecast_days"] = weather_params["forecast_days"]
    
    if historical:
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        params["start_date"] = start_date
        params["end_date"] = end_date
    
    responses = openmeteo.weather_api(url, params=params)
    
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    if forecast_reso == "hourly":
        response_data = response.Hourly()
    elif forecast_reso == "minutely_15":
        response_data = response.Minutely15()
    
    return response_data, response.Timezone().decode()
