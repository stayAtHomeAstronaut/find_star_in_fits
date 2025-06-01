import sys
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats


def fixdata(csv_file_path,r_avg_mins):
    pddf = pd.read_csv(csv_file_path, header=0)
    #pddf = pd.read_csv('WASP-12_TYC_1891-188-1_rgb_output.csv', header=0)


    #print(pddf)
    pddf.set_index('obs_date_time', inplace=True)
    pddf.index = pd.to_datetime(pddf.index)

    q_low = (pddf["target_flux_red"]  + pddf["flux_blue"]).quantile(0.01)
    q_hi  = (pddf["target_flux_red"] + pddf["flux_blue"]).quantile(0.95)
    pddf = pddf[((pddf["target_flux_red"]  + pddf["flux_blue"]) < q_hi) & ((pddf["target_flux_red"]  + pddf["flux_blue"]) > q_low)]
    
    
    target_flux_average = ((pddf["target_flux_red"]  + pddf["flux_blue"]) * pddf["airmass"]).mean()
    pddf["blue_over_red"] = ((((pddf["flux_blue"]) /pddf["target_flux_red"])**20 * pddf["airmass"]) + target_flux_average ).rolling(r_avg_mins).mean()
    pddf.insert(3,'target_total_flux',(((pddf["target_flux_red"] + pddf["flux_blue"]) * pddf["airmass"])).rolling(r_avg_mins).mean())
    pddf["target_flux_red"] = (pddf["target_flux_red"]  * pddf["airmass"]).rolling(r_avg_mins).mean()
    pddf["flux_blue"] = (pddf["flux_blue"]  * pddf["airmass"]).rolling(r_avg_mins).mean()
    pddf["airmass"] = pddf["airmass"].rolling(r_avg_mins).mean()


    print(pddf[['target_total_flux','blue_over_red']])
    shift_delta_max = (pddf['target_total_flux'].max()) / (pddf['blue_over_red'].max())
    print(shift_delta_max)
    for scale_exponent in range(1,125):
        pddf["blue_over_red"] = ((pddf["flux_blue"] /pddf["target_flux_red"])**scale_exponent) + target_flux_average
        shift_delta_max = (pddf['target_total_flux'].max()) / (pddf['blue_over_red'].max())
        if shift_delta_max < 0.95:
            print("scale_exponent " + str(scale_exponent) + " shift_delta_max: " + str(shift_delta_max))
            break
    
    
    pddf["blue_over_red"].plot(kind='line', color='purple')
    pddf["airmass"].plot(kind='line', color='lightgrey',linestyle='dashdot')
    pddf["flux_blue"].plot(kind='line', color='blue')
    pddf["target_flux_red"].plot(kind='line', color='red')
    pddf["target_total_flux"].plot(kind='line', color='black')

    sz_label = 'Rolling ' + str(r_avg_mins) + ' minute average'
    plt.title("Target Name: " + pddf["target_name"][0])
    plt.xlabel(sz_label)
    plt.ylabel('Blue/Red Flux Ratio (Purple)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_dat.py <CSV_file_name> <minutes_for_rolling_average> (default: 15)")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    if len(sys.argv)==3  :
        r_avg_mins = int(sys.argv[2])
    else:
        r_avg_mins = 15

    fixdata(csv_file_path,r_avg_mins)
