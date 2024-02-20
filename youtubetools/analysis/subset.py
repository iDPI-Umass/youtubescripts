import pandas as pd
from youtubetools.config import ROOT_DIR
from youtubetools.analysis.summarize import CollectionSummarizer
from youtubetools.analysis.langanalysis import create_subset_collections, load_metadata


collection = "combined"
df = load_metadata(collection)

language = "en"
confidence = 0.95

high_confidence = df[(df["whisper_lang"] == language) & (df["whisper_probability"] > confidence)].reset_index(drop=True)
low_confidence = df[(df["whisper_lang"] == language) & (df["whisper_probability"] <= confidence)].reset_index(drop=True)

create_subset_collections(high_confidence, f"{language}_high", folder=collection)
create_subset_collections(low_confidence, f"{language}_low", folder=collection)


