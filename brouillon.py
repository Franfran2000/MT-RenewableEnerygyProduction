# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:54 2026

@author: Francis Jacobs
"""
import pvlib.pvsystem as pvsyst

sandia_modules = pvsyst.retrieve_sam('SandiaMod')
print(sandia_modules.columns)

modules = ["Panasonic_VBHN235SA06B__2013_", 'Trina_TSM_240PA05__2013_', "Canadian_Solar_CS5P_220M___2009_"]

print(sandia_modules[modules])

import pvlib

from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem, Array
from pvlib.pvsystem import FixedMount, SingleAxisTrackerMount

from RenewModule import RenewModule


class PVModule(RenewModule):

    def __init__(self, location):
        super().__init__()

        self.location = Location(**location)
        self.arrays = []
        self.system = None
        self.modelchain = None

    def read_params(
        self,
        arrays,
        inverter_name,
        temperature_model=("sapm", "open_rack_glass_glass"),
    ):

        sandia_modules = pvlib.pvsystem.retrieve_sam("SandiaMod")
        sapm_inverters = pvlib.pvsystem.retrieve_sam("cecinverter")

        inverter = sapm_inverters[inverter_name]

        temp_family, temp_config = temperature_model
        temp_params = (
            pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS
            [temp_family][temp_config]
        )

        self.arrays = []

        for cfg in arrays:

            module = sandia_modules[cfg["module"]]

            # -----------------------------
            # Select mount
            # -----------------------------

            if cfg["mount"] == "fixed":

                mount = FixedMount(
                    surface_tilt=cfg["surface_tilt"],
                    surface_azimuth=cfg["surface_azimuth"],
                )

            elif cfg["mount"] == "tracker":

                mount = SingleAxisTrackerMount(
                    axis_tilt=cfg.get("axis_tilt", 0),
                    axis_azimuth=cfg.get("axis_azimuth", 180),
                    max_angle=cfg.get("max_angle", 90),
                    backtrack=cfg.get("backtrack", True),
                    gcr=cfg.get("gcr", 0.35),
                )

            else:
                raise ValueError(f"Unknown mount type: {cfg['mount']}")

            array = Array(
                mount=mount,
                module_parameters=module,
                temperature_model_parameters=temp_params,
                modules_per_string=cfg.get("modules_per_string", 1),
                strings=cfg.get("strings", 1),
            )

            self.arrays.append(array)

        self.system = PVSystem(
            arrays=self.arrays,
            inverter_parameters=inverter,
        )

        self.modelchain = ModelChain.with_sapm(
            self.system,
            self.location,
        )

    def calculate_power(self, weather):

        self.modelchain.run_model(weather)

        self.power = self.modelchain.results.ac

        return self.power
    
    
arrays = [

    {
        "mount": "fixed",
        "module": "Canadian_Solar_CS5P_220M___2009_",

        "surface_tilt": 35,
        "surface_azimuth": 180,

        "modules_per_string": 10,
        "strings": 5,
    },

    {
        "mount": "fixed",
        "module": "Canadian_Solar_CS5P_220M___2009_",

        "surface_tilt": 20,
        "surface_azimuth": 90,

        "modules_per_string": 8,
        "strings": 6,
    },

    {
        "mount": "tracker",
        "module": "Canadian_Solar_CS5P_220M___2009_",

        "axis_tilt": 0,
        "axis_azimuth": 180,
        "max_angle": 60,
        "backtrack": True,
        "gcr": 0.30,

        "modules_per_string": 12,
        "strings": 8,
    },

]

pv = PVModule(location)

pv.read_params(
    arrays=arrays,
    inverter_name="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
)

power = pv.calculate_power(weather)

# Extending to bifacial

# The nice thing about this design is that adding bifacial support doesn't require changing the interface. You can simply add optional keys such as:

{
    "bifacial": True,
    "albedo": 0.25,
    "gcr": 0.35,
    "height": 1.5,
    "pitch": 6.0,
}

# Then, when building each Array, detect cfg.get("bifacial", False) and invoke the appropriate bifacial irradiance model before running the electrical model. This keeps the configuration extensible while leaving the public API unchanged.