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

