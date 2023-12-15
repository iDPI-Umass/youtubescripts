import os
import json
import pandas as pd
from youtubetools.config import ROOT_DIR

summary_files = [
    "combined.json",
    "combined_ar.json",
    "combined_en.json",
    "combined_es.json",
    "combined_hi.json",
    "combined_lowprob.json",
    "combined_pt.json",
    "combined_ru.json"
]

headers = []
quantiles = []
headers.append("percentile")
quantiles.append(pd.DataFrame(list(range(1, 100))))
for summary_file in summary_files:
    with open(os.path.join(ROOT_DIR, "summaries", summary_file), "r") as f:
        summary = json.load(f)
    for key in summary["stats"]["quantiles"]:
        quantile_df = pd.DataFrame(summary["stats"]["quantiles"][key])
        quantiles.append(quantile_df)
        headers.append(f'{key}_{summary_file.split(".json")[0]}')
print(quantiles)
df = pd.concat(quantiles, axis="columns", ignore_index=True)
with open(os.path.join(ROOT_DIR, "summaries", "combined_summaries.csv"), "w") as f:
    df.to_csv(f, header=headers)