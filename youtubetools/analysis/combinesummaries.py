import os
import csv
import json
import pandas as pd
from youtubetools.config import ROOT_DIR

# summary_files = [
#     "combined.json",
#     "combined_ar.json",
#     "combined_en.json",
#     "combined_es.json",
#     "combined_hi.json",
#     "combined_lowprob.json",
#     "combined_pt.json",
#     "combined_ru.json"
# ]

language = "ar"
languages = ["en", "hi", "es", "pt", "ru", "ar"]

for language in languages:
    summary_files = [
        f"combined_recs_{language}_root.json",
        f"combined_recs_{language}_1.json",
        f"combined_recs_{language}_2.json"
    ]

    headers = []
    quantiles = []
    languages = {"level": ["root", "1", "2"]}
    headers.append("percentile")
    quantiles.append(pd.DataFrame(list(range(1, 100))))
    for i in range(len(summary_files)):
        with open(os.path.join(ROOT_DIR, "summaries", summary_files[i]), "r") as f:
            summary = json.load(f)
        for key in summary["stats"]["quantiles"]:
            quantile_df = pd.DataFrame(summary["stats"]["quantiles"][key])
            quantiles.append(quantile_df)
            headers.append(f'{key}_{summary_files[i].split(".json")[0]}')

        for j in range(len(summary["stats"]["data"]["whisper_lang"]["labels"])):
            language_label = summary["stats"]["data"]["whisper_lang"]["labels"][j]
            if language_label not in languages.keys():
                languages[language_label] = [0, 0, 0]
            languages[language_label][i] = summary["stats"]["data"]["whisper_lang"]["values"][j]


    print(quantiles)
    df = pd.concat(quantiles, axis="columns", ignore_index=True)
    with open(os.path.join(ROOT_DIR, "summaries", f"combined_{language}_summaries.csv"), "w") as f:
        df.to_csv(f, header=headers)

    print(languages)
    pd.DataFrame(languages).to_csv(os.path.join(ROOT_DIR, "summaries", f"combined_{language}_languages.csv"), index=False)


