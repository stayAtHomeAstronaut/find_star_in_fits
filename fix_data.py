import matplotlib.pyplot as plt
import pandas as pd


pddf = pd.read_csv('/Users/dan/dev/find_star_in_fits/XO-6_TYC 4357-1174-1_rgb_output.csv', header=0)
print(pddf)
pddf.set_index('obs_date_time', inplace=True)
pddf.index = pd.to_datetime(pddf.index)
pddf = pddf.resample('min').mean().interpolate()
#pddf = pddf.resample('5min').mean().interpolate()
print(pddf)

q_low = pddf["blue_over_red"].quantile(0.01)
q_hi  = pddf["blue_over_red"].quantile(0.99)
pddf = pddf[(pddf["blue_over_red"] < q_hi) & (pddf["blue_over_red"] > q_low)]

pddf["blue_over_red"].rolling(30).mean().plot(kind='line', color='blue')
pddf["comp_blue_over_red"].rolling(30).mean().plot(secondary_y=True,kind='line', color='gray')
plt.xlabel('Julian Date')
plt.ylabel('Blue/Red Flux (ADU)')
plt.grid(True)
plt.show()
