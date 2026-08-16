"""
PV json example
"""

arrays = [
    {
        "module": "Canadian_Solar_CS5P_220M___2009_",
        "mount": {"type": "fixed", 
                  "params": {
                        "surface_tilt": 35,
                        "surface_azimuth": 180,
                        }
                  }, 
        "modules_per_string": 1,
        "strings": 1,
        "temperature_model": ("sapm", "open_rack_glass_glass")
    },
    {   
        "module": "Panasonic_VBHN235SA06B__2013_",
        "mount": {"type" :"tracker", 
                  "params": {
                        "axis_tilt": 0,
                        "axis_azimuth": 180,
                        "max_angle": 60,
                        "backtrack": True,
                        }
                  },
        "modules_per_string": 1,
        "strings": 1,
        "temperature_model": ("sapm", "open_rack_glass_glass")
    },
    {
        "module": "Silevo_Triex_U300_Black__2014_",
        "mount": {"type": "fixed", 
                  "params": {
                        "surface_tilt": 30,
                        "surface_azimuth": 180,
                        }
                  }, 
        "modules_per_string": 1,
        "strings": 1,
        "temperature_model": ("sapm", "open_rack_glass_polymer")
    },
]

system1 = { 
        "inverter_name": "iPower__SHO_5_2__240V_",
        "arrays": arrays
    }

system2 = { 
        "inverter_name": "Yes!_Solar__ES5000P__208V_",
        "arrays": arrays
    }

systems = [system1, system2]


location = {
    "latitude": 50.67,
    "longitude": 4.62,
    "name": "Louvain-la-Neuve",
    "altitude": 123,
    "tz": "Europe/Berlin",
    }


install1 = {
   "location": location,
    "systems": systems,
    }

install2 = {
   "location": location,
    "systems": systems,
    }

installs = [install1, install2]

config1 = {
    "type": "pv",
    "installations": installs
    }

config2 = {
    "type": "pv",
    "installations": installs
    }

configs_pv = {
    # "weather": {"start_date": "2022-01-01", "end_date": "2022-01-07", "forecast_reso": "minutely_15"},
    "weather": {"start_date": None, "end_date": None, "forecast_reso": "hourly"},
    "configs": [config1, config2]
} 


"""
Wind JSON example
"""

turbines = {
    "farm": True,
    "farm_name": "example_farm",
    "turbines": [{"number_of_turbines": 3, "turbine_data": {"turbine_type": "E-126/4200", "hub_height": 135}},
                 {"number_of_turbines": 2, "turbine_data": {"turbine_type":"N131/3000", "hub_height": 114}}],
    "efficiency": 0.9,
    "modelchain_params": {
        "wake_losses_model": "wind_farm_efficiency",
        # 'dena_mean' (default), None,
        # 'wind_farm_efficiency' or name
        #  of another wind efficiency curve
        #  see :py:func:`~.wake_losses.get_wind_efficiency_curve`
        "smoothing": True,  # False (default) or True
        "block_width": 0.5,  # default: 0.5
        "standard_deviation_method": "Staffell_Pfenninger",  #
        # 'turbulence_intensity' (default)
        # or 'Staffell_Pfenninger'
        "smoothing_order": "wind_farm_power_curves",  #
        # 'wind_farm_power_curves' (default) or
        # 'turbine_power_curves'
        "wind_speed_model": "logarithmic",
        # 'logarithmic' (default), 'hellman' or 'interpolation_extrapolation'
        "density_model": "ideal_gas",  #
        # 'barometric' (default), 'ideal_gas' or 'interpolation_extrapolation'
        "temperature_model": "linear_gradient",
        # 'linear_gradient' (def.) or 'interpolation_extrapolation'
        "power_output_model": "power_curve",
        # 'power_curve' (default) or 'power_coefficient_curve'
        "density_correction": True,  # False (default) or True
        "obstacle_height": 0,  # default: 0
        "hellman_exp": 1/7,
        }  # None (default) or None
    }

install1 = {
    "location": location,
    "turbines": turbines,
    }

install2 = {
    "location": location,
    "turbines": turbines,
    }

installs = [install1, install2]

config1 = {
    "type": "wind",
    "installations": installs
    }

config2 = {
    "type": "wind",
    "installations": installs
    }

configs_wind = {
    "weather": {"start_date": None, "end_date": None, "forecast_reso": "minutely_15"},
    "configs": [config1, config2]
}

import json 

json_pv = json.dumps(configs_pv, indent=4)
with open("pv.json", "w") as f:
    f.write(json_pv)

json_wind = json.dumps(configs_wind, indent=4)
with open("wind.json", "w") as f:
    f.write(json_wind)

from main import main
import matplotlib.pyplot as plt

results = main(["wind.json"])

powers = results["simulated_power_outputs"]
 # plots
for config_power in powers:
    for config_type, config_modules in config_power.items():
        power = config_modules[0].get_power()
        for power_module in config_modules[1:]:
            power += power_module.get_power()
        
        config_type = config_type[:-len("_modules")]
        (power/1000).plot()
        plt.title(f"Simulated {config_type} power output")
        plt.xlabel("Date")
        plt.ylabel(f"Power (kW)")
        plt.show()
        
        energy = power.sum()*0.25/1000 # [kWh] 15 minute interval, not whole hour
        print("Simulated total energy output", energy, "kWh")
        