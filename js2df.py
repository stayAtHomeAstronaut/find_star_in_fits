import sys
import json
import pandas as pd

def read_and_put_into_dataframe(json_file_path):
    star_data_df = pd.read_json(json_file_path)
    print(star_data_df)
    for index, row in star_data_df.iterrows():
        if {row['target_comp']} == 'target':
            print(f"Index: {index} is target")
            print(f" {row['star_name']}")
            target_name = {row['star_name']}
            target_ra = {row['ra_degrees']}  # RA in degrees
            target_dec = {row['dec_degrees']}  # DEC in degrees
        else:
            print(f"Index: {index} is comp")
            print(f" {row['star_name']}")
            comp_name = {row['star_name']}
            comp_ra = {row['ra_degrees']}  # RA in degrees
            comp_dec = {row['dec_degrees']}  # DEC in degrees



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python js2df.py <json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    read_and_put_into_dataframe(json_file_path)
