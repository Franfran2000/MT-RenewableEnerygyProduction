"""
Green_bizz comparing file
"""

import pandas as pd
from main import main


folder = "./GreenBizz_Sibelga"
path = "GB_Sibelga_2022_01.csv"

dataframe = pd.read_csv(folder+"/"+ path)

dataframe["date"] = pd.DatetimeIndex(dataframe["Unnamed: 0"])

dataframe.drop(columns="Unnamed: 0", inplace=True)
dataframe.set_index("date", inplace=True)

from matplotlib import pyplot as plt

power = dataframe["Greenbizz injection"]
power.plot()
plt.xlabel("Date")
plt.ylabel("Power injection (W)")
plt.show()

# Modélisation
# From data, needs to handle 240kWp of DC input power
# Inverter chosen: Xantrex_Technology__PV225S_480__480V_
# Nominal AC power = 227.3kWp
# Nominal DC power needed = 241730.812 kWp
# Nominal DC input voltage = 368, used to determine string size

# Solar Module chosen:
# From data, installation has 943 modules -> nominal power of 255W per panel
# Module chosen: Schott_Solar_ASE_270_DGF_50__260___2007__E__
# Nominal power = 258.11W
# Voltage at max power = 48.7V
# to reach 368V, need 7 panels (in series) per string
# to reach 943 panels, need 135 strings in parallel -> 945 total panels

arrays = [{
    "module": "Schott_Solar_ASE_270_DGF_50__260___2007__E__",
    "mount": {"type": "fixed", 
              "params": {
                    "surface_tilt": 0,
                    "surface_azimuth": 233,
                    }
              }, 
    "modules_per_string": 7,
    "strings": 135,
    "temperature_model": ("sapm", "close_mount_glass_glass")
    
    }]
systems = [{
    "inverter_name": "Xantrex_Technology__PV225S_480__480V_",
    "arrays": arrays
    }]

# Assumed 10 tall building for altitude
location = {
    "latitude": 50.8709166667,
    "longitude": 4.3503055556,
    "name": "Greenbizz",
    "altitude": 33,
    "tz": "Europe/Berlin",
    }

installs = [{
    "location": location,
    "systems": systems
    }]

configs = [{
    "type": "pv",
    "installations": installs
    }]

weather = {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "forecast_reso": "minutely_15"
    }

configs_pv = {
    "weather": weather,
    "configs": configs
    }

import json 

json_pv = json.dumps(configs_pv, indent=4)
with open("greenbizz.json", "w") as f:
    f.write(json_pv)
    
main(["greenbizz.json"], consumption=power)