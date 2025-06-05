import sys
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from astropy.time import Time

def fixdata(csv_file_path,r_avg_mins):
    pddf = pd.read_csv(csv_file_path, header=0)
    target_name = pddf["target_name"][0]

    pddf = pddf.drop('obs_date_time',axis=1)
    pddf.insert(0, 'obs_date_time', Time(pddf.iloc[:, 0], format='jd').to_datetime())
    print(pddf)

    #pddf.set_index('obs_date_time', inplace=True)
    #pddf.index = pd.to_datetime(pddf.index)

    q_low = (pddf["target_flux_red"]  + pddf["flux_blue"]).quantile(0.01)
    q_hi  = (pddf["target_flux_red"] + pddf["flux_blue"]).quantile(0.95)
    q_blue_over_red_high = pddf["blue_over_red"].quantile(0.95)
    pddf = pddf[((pddf["target_flux_red"]  + pddf["flux_blue"]) < q_hi) & ((pddf["target_flux_red"]  + pddf["flux_blue"]) > q_low) & ((pddf["blue_over_red"]) < q_blue_over_red_high)]
    print("outliers removed")
    pddf.insert(4, 'comp_flux', (pddf["comp_flux_red"] + pddf["comp_flux_blue"]))
    pddf.insert(4, 'target_flux', (pddf["target_flux_red"] + pddf["flux_blue"]))
    pddf.insert(4, 'rel_flux', (pddf["target_flux"] / pddf["comp_flux"]))
    pddf = pddf[['obs_date_time','JD', 'target_name' , 'rel_flux', 'blue_over_red','comp_blue_over_red', 'target_flux' ,'comp_name' ,'comp_flux','airmass']]
    print(pddf)
    pddf[['rel_flux', 'blue_over_red','comp_blue_over_red', 'target_flux' ,'comp_flux','airmass']] = pddf[['rel_flux', 'blue_over_red','comp_blue_over_red', 'target_flux' ,'comp_flux','airmass']].rolling(window=r_avg_mins).mean()
    pddf = pddf.dropna()
    pddf.insert(10,'rolling_average_window_size',r_avg_mins)
    print(pddf)
    outfile = target_name.replace(" ","-") + '-rolling_average_output.csv'
    pddf.to_csv(outfile, index=False)
    

    pddf["blue_over_red"].plot(kind='line', color='purple')
    pddf["rel_flux"].plot(kind='line', color='red')
    pddf["comp_blue_over_red"].plot(kind='line', color='blue')

    sz_label = 'Rolling ' + str(r_avg_mins) + ' minute average'
    plt.title(target_name)
    plt.xlabel(sz_label)
    plt.ylabel('Blue/Red Flux Ratio (Purple)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_dat.py <CSV_file_name> <minutes_for_rolling_average> (default: 10)")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    if len(sys.argv)==3  :
        r_avg_mins = int(sys.argv[2])
    else:
        r_avg_mins = 10

    fixdata(csv_file_path,r_avg_mins)
