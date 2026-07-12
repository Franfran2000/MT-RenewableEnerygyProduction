"""
Module for Wind power forecast
"""

from RenewModule import RenewModule


from windpowerlib import ModelChain, WindTurbine
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class WindModule(RenewModule):
    
    def __init__(self):
        super().__init__()
        self.turbines = []
        
        self.mc = None
        
        
    def read_params(self, args, kwargs):
        pass
    
    def calculate_power(self, weather):
        