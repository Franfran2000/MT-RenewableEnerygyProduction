"""
Module for predicting power output of renewable energy sources
"""

import requests

# https://api.forecast.solar/estimate/watts/:lat/:lon/:dec/:az/:kwp
base_url = "https://api.forecast.solar/estimate"

# https://api.forecast.solar/check/:lat/:lon
check_url = "https://api.forecast.solar/check"


# Coordinates of Sainte-Barbe
latitude = 50.67 
longitude = 4.62

# Dummy values
declination = 20
azimuth = 0
module_power = 12.34 #Kilo watts

def format_url(base, lat, lon, dec="", az="", kwp=""):
    formatted_url = "{0}/{1}/{2}/{3}/{4}/{5}".format(base, lat, lon, dec, az, kwp)
    return formatted_url.strip("/")


url1 = format_url(check_url, latitude, longitude, declination, azimuth, module_power)

r1 = requests.get(url1)

print(r1.url)
print(r1.text)

# url2 = 
# r2 = requests.get()