"""
Module for Wind power forecast
"""

from RenewModule import RenewModule


from windpowerlib import ModelChain, WindTurbine, create_power_curve
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class WindModule(RenewModule):
    
    def __init__(self):
        super().__init__()
        
    def read_params(self, args, kwargs):
        pass
    
    