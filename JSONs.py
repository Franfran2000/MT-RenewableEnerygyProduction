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
        "module": "Panasonic_VBHN235SA06B__2013_",
        "mount": {"type": "fixed", 
                  "params": {
                        "surface_tilt": 30,
                        "surface_azimuth": 180,
                        }
                  }, 
        "temperature_model": ("sapm",  "open_rack_glass_polymer")
    },
]

system1 = { 
        "inverter_name": "iPower__SHO_5_2__240V_",
        "arrays": arrays
    }

system2 = { 
        "inverter_name": "iPower__SHO_5_2__240V_",
        "arrays": arrays
    }