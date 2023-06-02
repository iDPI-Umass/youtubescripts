import os
import pandas as pd
from youtubetools.config import ROOT_DIR


def import_collection_metadata(collection):
    df = pd.read_csv(os.path.join(ROOT_DIR, "collections", collection, "metadata.csv"))
    return df

def collection_comparison(c1, c2):
    c1_metadata = import_collection_metadata(c1)
    c2_metadata = import_collection_metadata(c2)

