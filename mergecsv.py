import os
import argparse
import pandas as pd
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("collections", nargs='*', type=str)
args = parser.parse_args()

dataframes = []


for collection in args.collections:
    if collection in os.listdir("collections"):
        csv_file = [file for file in os.listdir(os.path.join("collections", collection)) if file.endswith(".csv") and "metadata" in file][0]
        df = pd.read_csv(os.path.join("collections", collection, csv_file))
        dataframes.append(df)

combined_df = pd.concat(dataframes, ignore_index=True)
combined_df.to_csv(f"~/{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.csv")
