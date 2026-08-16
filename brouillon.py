# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:54 2026

@author: Francis Jacobs
"""
# import pvlib.pvsystem as pvsyst

# sandia_modules = pvsyst.retrieve_sam('SandiaMod')
# print(sandia_modules.columns)

# modules = ["Panasonic_VBHN235SA06B__2013_", 'Trina_TSM_240PA05__2013_', "Canadian_Solar_CS5P_220M___2009_"]

# import pvlib.pvsystem as psys
# import pandas as pd
# inverter_data = psys.retrieve_sam("CECInverter")

# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     inverters = inverter_data.transpose()
#     inverters.sort_values(["Paco"], inplace=True, ascending=False)
    
#     # print(inverters.loc[(inverters['Pdco'] >= 240000) & (inverters['Pdco'] <= 260000)][["Paco", "Pdco", "Vdco"]])

    
# sandia_modules = psys.retrieve_sam('SandiaMod')
# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     # print(sandia_modules.head(10)["Aleo_S16_170__2007__E__"])
    
#     panels = sandia_modules.transpose()
#     panels["Power"] = panels["Impo"]*panels["Vmpo"]
#     panels.sort_values(["Power"], ascending=False, inplace=True)    
#     print(panels[["Area", "Power", "Vmpo"]])
    
#    # print(panels["Vintage"])
    
# import pandas as pd

# # Create sample Series
# data1 = [1, 2, 3, 4]
# data2 = [5, 6, 7, 8]
# data3 = [9, 10, 11, 12]

# series1 = pd.Series(data1)
# series2 = pd.Series(data2)
# series3 = pd.Series(data3)

# # Sum of N Series with pd.concat
# result = pd.concat([series1, series2, series3], axis=1).sum(axis=1)
# print(result)

# import pandas as pd

# data = pd.read_csv("./Stockel_Sibelga 1/Stockel_Sibelga_202205.xlsx - Export.csv")
# print(data.columns)

# forecast_reso1 = "hourly"
# forecast_reso2 = "minutely_15"

# dic = {forecast_reso1: forecast_reso2}
# print(dic)

# import pvlib
# print(pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"])

import pandas as pd
df = pd.read_csv("31July2021.csv")
df.drop(columns=["No Science"], inplace=True)

new_df = pd.read_csv("Old 31Jul2022.csv")
print(new_df)

df["Unnamed: 0"] = new_df["Unnamed: 0"]

print(df)
df.to_csv("31July2022.csv", index=False)

