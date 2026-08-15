"""
Green_bizz comparing file
"""
import glob
import pandas as pd
from main import main

folder = glob.glob("./GreenBizz_Sibelga/*.csv")

dataframes = []

for file_path in folder:    
    monthly_data = pd.read_csv(file_path)
    dataframes.append(monthly_data)
#%%   
##### Create global dataframe with all datapoints, set datetime as index
df = pd.concat(dataframes, verify_integrity=True, ignore_index=True)
df["date"] = pd.DatetimeIndex(df["Unnamed: 0"])
df.drop(columns="Unnamed: 0", inplace=True)
df.set_index("date", inplace=True)

# Data is in the form of 15 minute intervals of energy produced and consumed [kWh]
# The amount of power needed to produce this amount of energy in 15min equals:
# Power = 1000*Energy/Time, energy in [kWh], Time in 0.25[h]  
# Power [W] = 1000*energy/0.25

df = df*1000*4

######## TIMELINE CHOOSING
start_date = "2021-10-01"
end_date = "2022-09-30"

df = df.loc[(df.index >= start_date) & (df.index <= end_date + " 23:45:00")]

print(df)

from matplotlib import pyplot as plt

power_injected = df["Greenbizz injection"]
power_injected.plot()
plt.title("Daily Greenbizz power injection")
plt.xlabel("Date")
plt.ylabel("Power injection (W)")
plt.show()

print("Greenbizz total energy injected", power_injected.sum()*0.25/1000, "kWh")

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

# Assumed 10m tall building for altitude
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
    "start_date": start_date,
    "end_date": end_date,
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

consumption_data = df.drop(columns="Greenbizz injection")

consumption_data = consumption_data

results = main(["greenbizz.json"], consumption=consumption_data)