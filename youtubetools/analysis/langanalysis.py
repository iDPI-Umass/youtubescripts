import os
import json
import numpy as np
import pandas as pd
from youtubetools.analysis.summarize import CollectionSummarizer
from youtubetools.config import ROOT_DIR, collection_init


def load_metadata(collection):
    metadata_csv = [file for file in os.listdir(os.path.join(ROOT_DIR, "collections", collection)) if file.endswith(".csv")]
    if len(metadata_csv) == 1:
        df = pd.read_csv(os.path.join(ROOT_DIR, "collections", collection, metadata_csv[0]))
        df_live = df[df["channel_id"] == "0"]
        live_videos_count = len(df_live)
        df = df[df["channel_id"] != "0"]
        df["upload_date"] = pd.to_datetime(df["upload_date"]) # , format="%m/%d/%y")
        df["upload_year"] = df["upload_date"].dt.year
        df = df.replace('', np.nan).fillna(0)
        return df
    else:
        raise Exception("multiple or no CSV files available in collection")


def create_subset_collections(subset_df: pd.DataFrame, folder_suffix: str, queries=None, efficiency=None, folder="combined"):
    if not os.path.isdir(os.path.join(ROOT_DIR, "collections", f"{folder}_{folder_suffix}")):
        collection_init(f"{folder}_{folder_suffix}")
    with open(os.path.join(ROOT_DIR, "collections", f"{folder}_{folder_suffix}", "collection_metadata.csv"), "w") as f:
        subset_df.to_csv(f)
    if queries is not None and efficiency is not None:
        subset_hits = len(subset_df)
        subset_size = (2**64) / (queries*efficiency/subset_hits)
        with open(os.path.join(ROOT_DIR, "collections", f"{folder}_{folder_suffix}", "sample_stats.json"), "w") as f:
            subset_stats = {
                "collection_date": f"{folder}_{folder_suffix}",
                "size": subset_size,
                "queries": queries,
                "hits": subset_hits,
                "prefix_len": 5,
                "efficiency": efficiency
            }
            json.dump(subset_stats, f, indent=4)


def main():
    df = pd.DataFrame()
    # collections = ["random_prefix_25000_20231220_150455_192679", "random_prefix_25000_20231220_051525_283405", "random_prefix_25000_20231219_191558_022207"]
    collections = ["random_prefix_25000_20231221_005140_165302", "random_prefix_25000_20231220_051525_283405",
                   "random_prefix_25000_20231220_150455_192679", "random_prefix_25000_20231219_191558_022207"]
    dfs = []
    queries, hits, efficiency = 0, 0, 0
    for collection in collections:
        dfs.append(load_metadata(collection))
        with open(os.path.join(ROOT_DIR, "collections", collection, "sample_stats.json")) as f:
            sample_stats = json.load(f)
            queries += sample_stats["queries"]
            hits += sample_stats["hits"]
            efficiency = sample_stats["efficiency"]

    size_estimate = (2**64) / (queries*efficiency/hits)
    print(size_estimate)
    df = pd.concat(dfs, ignore_index=True)
    print(df)
    with open(os.path.join(ROOT_DIR, "collections", "combined", "collection_metadata.csv"), "w") as f:
        df.to_csv(f)
    with open(os.path.join(ROOT_DIR, "collections", "combined", "sample_stats.json"), "w") as f:
        json.dump({"collection_date": "combined", "size": int(size_estimate), "queries": queries, "hits": hits, "prefix_len": 5, "efficiency": efficiency}, f, indent=4)

    collection_summarizer = CollectionSummarizer("combined")
    collection_summarizer.calculate_collection_stats()
    print(json.dumps(collection_summarizer.export_collection_stats(), indent=4))

    create_subset_collections(df[df["whisper_probability"] < 0.75], "lowprob", queries, efficiency)
    collection_summarizer = CollectionSummarizer(f"combined_lowprob")
    collection_summarizer.calculate_collection_stats()
    print(json.dumps(collection_summarizer.export_collection_stats(), indent=4))

    combined_summarizer = CollectionSummarizer("combined")
    combined_summarizer.calculate_collection_stats()
    print(json.dumps(collection_summarizer.export_collection_stats(), indent=4))

    languages = ["en", "hi", "es", "pt", "ru", "ar"]
    for language in languages:
        create_subset_collections(
            df[(df["whisper_lang"] == language) & (df["whisper_probability"] >= 0.75)],
            language,
            queries,
            efficiency
        )
        collection_summarizer = CollectionSummarizer(f"combined_{language}")
        collection_summarizer.calculate_collection_stats()
        print(json.dumps(collection_summarizer.export_collection_stats(), indent=4))


if __name__ == '__main__':
    main()