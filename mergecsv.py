import os
import argparse
import pandas as pd
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("collections", nargs='*', type=str)
args = parser.parse_args()

dataframes = []
collections = args.collections
if len(args.collections) == 1 and args.collections[0] == "all":
    collections = [collection for collection in os.listdir("collections") if not collection.startswith(".")
                   and os.path.isdir(os.path.join("collections", collection))]

for collection in collections:
    if collection in os.listdir("collections"):
        csv_files = [file for file in os.listdir(os.path.join("collections", collection)) if file.endswith(".csv") and "metadata" in file]
        if len(csv_files) > 0:
            print(collection)
            csv_file = csv_files[0]
            df = pd.read_csv(os.path.join("collections", collection, csv_file))
            dataframes.append(df)

combined_df = pd.concat(dataframes, ignore_index=True)
combined_df.to_csv(f"~/{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.csv")
