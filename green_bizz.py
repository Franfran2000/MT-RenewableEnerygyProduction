"""
Green_bizz comparing file
"""
import glob
import pandas as pd
from IPython.display import display
from main import main

## Error measurement
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

folder = glob.glob("./GreenBizz_Sibelga/*.csv")

dataframes = []

for file_path in folder:    
    monthly_data = pd.read_csv(file_path)
    dataframes.append(monthly_data)
#%%   
### PREPROCESS
##### Create global dataframe with all datapoints, set datetime as index
df = pd.concat(dataframes, verify_integrity=True, ignore_index=True)
df["date"] = pd.DatetimeIndex(df["Unnamed: 0"])
df.drop(columns="Unnamed: 0", inplace=True)
df.set_index("date", inplace=True)

df["No Science"] = df["No Science"].fillna(0) # There are no longer "No Science" data after 01 May 2022, resulting in a column filled with NaN
df["Citydev"] = df["Citydev"].fillna(0) # Citydev doesnt appear in data until 01 Oct 2021, NaN before that

df.fillna(0, inplace=True) # 31st July 2022 has no datapoints at all, set to 0

# Data is in the form of 15 minute intervals of energy produced and consumed [kWh]
# The amount of power needed to produce this amount of energy in 15min equals:
# Power = 1000*Energy/Time, energy in [kWh], Time in 0.25[h]  
# Power [W] = 1000*energy/0.25

w_to_kwh = 0.25/1000 # 1000W = kW, 15 minute intervals -> energy production of 1kW for 15min = 1kW*h/4
df = df/w_to_kwh

######## TIMELINE CHOOSING
start_date = "2021-10-01"
end_date = "2022-09-30"

df = df.loc[(df.index >= start_date) & (df.index <= end_date + " 23:45:00")]

nan_df = df.isnull().values
nan_indices = []
for i in range(len(nan_df)):
    if nan_df[i].any():
        nan_indices.append(i)
pd.set_option('display.max_columns', None)
display(df.iloc[nan_indices])

from matplotlib import pyplot as plt

power_injected = df["Greenbizz injection"]
(power_injected/1000).plot()
plt.title("Daily Greenbizz power injection")
plt.xlabel("Date")
plt.ylabel("Power injection (kW)")
plt.show()

print("Greenbizz total energy injected", power_injected.sum()*w_to_kwh, "kWh")

nan_list = power_injected.isnull().values
nan_indices = []
for i in range(len(nan_list)):
    if nan_list[i]:
        nan_indices.append(i)

print(nan_indices)

# Modeling
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
results = main(["greenbizz.json"], consumption=consumption_data)

powers = results["simulated_power_outputs"]
self_cons = results["self_consumption"]

 # plots
for config_power in powers:
    for config_type, config_modules in config_power.items():
        power = config_modules[0].get_power()
        for power_module in config_modules[1:]:
            power += power_module.get_power()
        
        config_type = config_type[:-len("_modules")]
        (power/1000).plot()
        plt.title(f"Daily simulated {config_type} power output")
        plt.xlabel("Date")
        plt.ylabel(f"Power (kW)")
        plt.show()
        
        energy = power.sum()*w_to_kwh # [kWh] 15 minute interval, not whole hour
        print("Simulated total energy output", energy, "kWh")
        
total_cons = consumption_data.sum(axis=1)
(total_cons/1000).plot() # kW instead of W
plt.title("Daily power consumption")
plt.xlabel("Date")
plt.ylabel("Power consumption (kW)")
plt.show()

(self_cons/1000).plot()
plt.title("Daily self consumption")
plt.xlabel("Date")
plt.ylabel("Self consumption (kW)")
plt.show()

injection = power - self_cons

(injection/1000).plot()
plt.title("Daily simulated injection")
plt.xlabel("Date")
plt.ylabel("Simulated injection (kW)")
plt.show()

print("total actual consumed energy", total_cons.sum()*w_to_kwh, "kWh")
print("Total self-consumption energy", self_cons.sum()*w_to_kwh, "kWh")
print("Total injection energy", injection.sum()*w_to_kwh, "kWh")

print(injection.isnull().values.any())

injection_rmse = np.sqrt(mean_squared_error(power_injected/1000, injection/1000))
injection_mae = mean_absolute_error(power_injected/1000, injection/1000)

print(f"RMSE: {injection_rmse:.2f} kW")
print(f"MAE:  {injection_mae:.2f} kW")