import sys
import pandas as pd
from astropy.time import Time
import matplotlib.pyplot as plt

def exotic_extract(csv_file_path):

    # Step 1: Extract star name from line 8
    with open(csv_file_path, 'r') as f:
        lines = f.readlines()
        star_name = None
        for line in lines[:24]:
            if line.startswith("#STAR_NAME="):
                star_name = line.strip().split("=")[1]
                break

    if star_name is None:
        raise ValueError("STAR_NAME not found in the file header.")

    # Step 2: Read column headings and data
    df = pd.read_csv(csv_file_path, comment='#', skiprows=24)
    df.columns = ['JD','DIFF','ERR','DETREND_1','DETREND_2']
    df.insert(0, 'obs_date_time', Time(df.iloc[:, 0], format='jd').to_datetime())
    df.insert(2, 'star_name', star_name)
    print(df)
    # Step 5: Save DataFrame to CSV
    output_csv = star_name + '_exotic_data.csv'
    df.to_csv(output_csv, index=False)

    print(f"Data processed and saved to: {output_csv}")
    df['DIFF'].plot(kind='bar', color='black')
    df['DETREND_1'].plot(kind='line', color='red')
    df['DETREND_2'].plot(kind='line', color='blue')
    df['ERR'].plot(kind='line', color='green')
    sz_label = 'EXOTIC lightcurve data'
    plt.title("Target Name: " + df["star_name"][0])
    plt.xlabel(sz_label)
    plt.ylabel(' (Purple)')
    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exotic_extract.py <CSV_file_name>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    exotic_extract(csv_file_path)

