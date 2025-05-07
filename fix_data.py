import sys
import matplotlib.pyplot as plt
import pandas as pd



def fixdata(csv_file_path):
    pddf = pd.read_csv(csv_file_path, header=0)
    #pddf = pd.read_csv('WASP-12_TYC_1891-188-1_rgb_output.csv', header=0)


    print(pddf)
    pddf.set_index('obs_date_time', inplace=True)
    pddf.index = pd.to_datetime(pddf.index)
    #pddf = pddf.resample('min').mean().interpolate()
    #pddf = pddf.resample('5min').mean().interpolate()
    print(pddf)
    q_low = (pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]).quantile(0.01)
    q_hi  = (pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]).quantile(0.99)
    pddf = pddf[((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]) < q_hi) & ((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"]) > q_low)]
    print(pddf)


    r_avg_mins = 15
    (pddf["airmass"]*1000000 ).rolling(r_avg_mins).mean().plot(kind='line', color='lightgrey',linestyle='dashdot')

    (pddf["blue_over_red"]*1000000).rolling(r_avg_mins).mean().plot(kind='line', color='purple')
    ((pddf["target_flux_red"] + pddf["flux_green"] + pddf["flux_blue"])/2).rolling(r_avg_mins).mean().plot(kind='line', color='black')
    (pddf["target_flux_red"] ).rolling(r_avg_mins).mean().plot(kind='line', color='red')
    (pddf["flux_green"] ).rolling(r_avg_mins).mean().plot(kind='line', color='green')
    (pddf["flux_blue"] ).rolling(r_avg_mins).mean().plot(kind='line', color='blue')


    (pddf["comp_blue_over_red"]*1000000).rolling(r_avg_mins).mean().plot(kind='line', color='purple',linestyle='--', label='Dashed')
    #(pddf["comp_flux_red"] ).rolling(r_avg_mins).mean().plot(kind='line', color='salmon',linestyle='--')
    #(pddf["comp_flux_green"] ).rolling(r_avg_mins).mean().plot(kind='line', color='lightgreen',linestyle='--')
    #(pddf["comp_flux_blue"] ).rolling(r_avg_mins).mean().plot(kind='line', color='lightblue',linestyle='--')
    #((pddf["comp_flux_red"] + pddf["comp_flux_green"] + pddf["comp_flux_blue"])/2).rolling(r_avg_mins).mean().plot(kind='line', color='darkgrey',linestyle='--', label='Dashed')
    sz_label = 'Rolling ' + str(r_avg_mins) + ' minute average'
    plt.title("Target Name: " + pddf["target_name"][0])
    plt.xlabel(sz_label)
    plt.ylabel('Blue/Red Flux Radio * 1m (Purple)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_dat.py <CSV_file_name> ")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]

    fixdata(csv_file_path)
