import os
import json
import pandas as pd
from youtubetools.config import ROOT_DIR
from youtubetools.analysis.summarize import CollectionSummarizer
from youtubetools.analysis.langanalysis import load_metadata, create_subset_collections

languages = ["en", "hi", "es", "pt", "ru", "ar"]

language = "en"

for language in languages:
    language_folder = os.path.join(ROOT_DIR, "collections", f"trees_{language}")
    tree_folders = [f"trees_{language}/{tree_folder}" for tree_folder in os.listdir(language_folder) if tree_folder.startswith("recs_")]
    root_dfs, rec_dfs, rec2_dfs = [], [], []
    for tree_folder in tree_folders:
        tree_folder_path = os.path.join(ROOT_DIR, "collections", tree_folder)
        with open(os.path.join(ROOT_DIR, "collections", tree_folder, "tree.json"), "r") as f:
            tree = json.load(f)
        root_id = list(set(tree.keys()))
        recs_ids = list(set(tree[root_id[0]].keys()))
        recs2_ids = []
        for rec_id in recs_ids:
            recs2_ids += list(set(tree[root_id[0]][rec_id].keys()))
        recs2_ids = list(set(recs2_ids))
        df = load_metadata(tree_folder)
        root_dfs.append(df[df['id'].isin(root_id)])
        rec_dfs.append(df[df['id'].isin(recs_ids)])
        rec2_dfs.append(df[df['id'].isin(recs2_ids)])

    dfs = [pd.concat(root_dfs, ignore_index=True), pd.concat(rec_dfs, ignore_index=True), pd.concat(rec2_dfs, ignore_index=True)]
    collections = [f"recs_{language}_root", f"recs_{language}_1", f"recs_{language}_2"]

    for i in range(3):
        create_subset_collections(dfs[i], collections[i])
        collection_summarizer = CollectionSummarizer(f"combined_{collections[i]}", rec_tree=True)
        collection_summarizer.calculate_collection_stats(lang_confidence=0)
        print(json.dumps(collection_summarizer.export_collection_stats(), indent=4))