import matplotlib.pyplot as plt
import pandas as pd


pddf = pd.read_csv('TYC 3455-628-1_NGC 4226_rgb_output.csv', header=0)
pddf = pd.read_csv('hatP20tyc1914-1285-1.rgb_output.csv', header=0)


print(pddf)
pddf.set_index('obs_date_time', inplace=True)
pddf.index = pd.to_datetime(pddf.index)
pddf = pddf.resample('min').mean().interpolate()
#pddf = pddf.resample('5min').mean().interpolate()
print(pddf)


q_low = (pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]).quantile(0.01)
q_hi  = (pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]).quantile(0.99)
#pddf = pddf[((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]) < q_hi) & ((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]) > q_low)]
#print(pddf)


(pddf["blue_over_red"]*1000000).rolling(30).mean().plot(kind='line', color='purple')
((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"])/2).rolling(30).mean().plot(kind='line', color='grey')
(pddf["target_flux_red"] *1.75).rolling(30).mean().plot(kind='line', color='red')
(pddf["flux_green"] *1.75).rolling(30).mean().plot(kind='line', color='green')
(pddf["flux_blue"] ).rolling(30).mean().plot(kind='line', color='blue')
#(pddf["comp_blue_over_red"]*2000000).rolling(30).mean().plot(secondary_y=True,kind='line', color='orange')

plt.xlabel('Julian Date')
plt.ylabel('Blue/Red Flux Radio * 1m (Purple')
plt.grid(True)
plt.show()
