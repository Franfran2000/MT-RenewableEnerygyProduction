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
        "temperature_model": ("sapm",  "open_rack_glass_glass")
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
        "temperature_model": ("sapm",  "open_rack_glass_glass")
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
        "temperature_model": ("sapm",  "open_rack_glass_polymer")
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

configs = [config1, config2]


import json 

json_obj = json.dumps(configs, indent=4)
with open("sample.json", "w") as f:
    f.write(json_obj)





















