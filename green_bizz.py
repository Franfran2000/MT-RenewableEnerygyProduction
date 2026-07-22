"""
Green_bizz comparing file
"""

import pandas as pd

folder = "./GreenBizz_Sibelga"
path = "GB_Sibelga_2022_01.csv"

dataframe = pd.read_csv(folder+"/"+ path)

print(dataframe.columns)

dataframe["date"] = pd.DatetimeIndex(dataframe["Unnamed: 0"])

dataframe.drop(columns="Unnamed: 0", inplace=True)
dataframe.set_index("date", inplace=True)
print(dataframe.head(3))


from matplotlib import pyplot as plt

power = dataframe["Greenbizz injection"]
power.plot()
plt.xlabel("Date")
plt.ylabel(f"Power injection (W)")
plt.show()
