import sys
import json
import pandas as pd

def read_and_put_into_dataframe(json_file_path):
    star_data_df = pd.read_json(json_file_path)
    print(star_data_df)
    star_data_df.head()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python js2df.py <json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    read_and_put_into_dataframe(json_file_path)
