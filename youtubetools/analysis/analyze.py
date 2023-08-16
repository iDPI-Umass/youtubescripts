"""
functions for analyzing and comparing collections
"""

import os
import pandas as pd
from scipy.spatial import distance
from youtubetools.logger import log_error
from youtubetools.config import BINS, ROOT_DIR, PROBABILITY_THRESHOLD

"""
all 
simple_attributes = ['id', 'title', 'fulltitle', 'thumbnail', 'description', 'average_rating', 'channel_id', 'channel',
                     'uploader', 'uploader_id', 'availability', 'live_status', 'is_live',
                     'was_live', 'age_limit', '_has_drm', '_type', 'whisper_probability',
                    'album', 'artist', 'track', 'release_date', 'release_year']
other_attributes = ['categories', 'tags', 'automatic_captions', 'subtitles', 'chapters']
"""


def calculate_vectors(metadata: pd.DataFrame, attribute: str) -> dict:
    """
    calculates vectors for one attribute in a collection's metadata
    :param metadata: a collection's metadata dataframe (use import_collection_metadata to import metadata)
    :param attribute: name of attribute to calculate vectors for
    :return: dict of bin labels keys, vector values
    """

    # initialize dict with bin labels
    ordered_binned_vectors = dict.fromkeys(BINS[attribute], 0)

    # calculate vectors for non-numerical bins
    if attribute in ["accessible_in_youtube_music", "whisper_lang"]:
        binned_vectors = metadata[attribute].value_counts(normalize=True).to_dict()
        for bin_label in binned_vectors:
            ordered_binned_vectors[bin_label] = binned_vectors[bin_label]
    # calculate vectors for numerical bins
    else:
        binned_vectors = metadata[attribute].value_counts(bins=BINS[attribute], normalize=True).to_dict()
        for bin_label in binned_vectors:
            # if isinstance(bin_label, pd._libs.interval.Interval):
            # use left side of interval as bin label
            ordered_binned_vectors[int(bin_label.left)] = binned_vectors[bin_label]
    return ordered_binned_vectors


def import_collection_metadata(collection: str) -> pd.DataFrame:
    """
    imports collection_metadata.csv as a dataframe
    :param collection: folder name of collection
    :return: data from collection_metadata.csv in a dataframe
    """
    try:
        metadata_filename = [f for f in os.listdir(os.path.join(ROOT_DIR, "collections", collection))
                             if f.endswith(".csv")][0]
        df = pd.read_csv(os.path.join(ROOT_DIR, "collections", collection, metadata_filename))
        df = df.drop(df[df['upload_date'] != df['upload_date']].index)
        df['upload_year'] = df['upload_date'].apply(lambda x: int("20"+x[-2:]))
        df.loc[df['whisper_probability'] < PROBABILITY_THRESHOLD, 'whisper_lang'] = 'xx'
        return df
    except Exception as e:
        log_error(collection, "xxxxxxxxxxx", "analysis.import_collection_metadata", str(e))
    return pd.DataFrame()


def get_vector_headers(attributes: list) -> list:
    """
    assembles list of vector bin labels for a list of attributes
    :param attributes: list of attributes
    :return: list of vector bin labels
    """
    headers = []
    for attribute in attributes:
        headers += BINS[attribute]
    return headers


def collection_comparison(c1: str, c2: str, attributes=None):
    """
    calculates cosine similarity between two collections of YouTube videos
    :param c1: folder name of collection1
    :param c2: folder name of collection2
    :param attributes: str list of attributes to compare
    :return:
        cosine_similarity: float
        used_attributes: str list of attributes compared
        get_vector_headers(used_attributes): str list of vector bins
        c1_vectors: float list of collection1 vectors
        c2_vectors: float list of collection2 vectors
    """
    # default attributes to compare
    if attributes is None:
        attributes = ['view_count', 'duration', 'upload_year', 'accessible_in_youtube_music', 'whisper_lang']

    # import metadata and initialize headers/vectors
    c1_metadata, c2_metadata = import_collection_metadata(c1), import_collection_metadata(c2)
    c1_headers, c2_headers = c1_metadata.columns.values.tolist(), c2_metadata.columns.values.tolist()
    c1_vectors, c2_vectors, used_attributes = [], [], []

    for attribute in attributes:
        # only compare an attribute if it's available in the metadata for both collections
        if attribute in c1_headers and attribute in c2_headers:
            c1_vectors += list(calculate_vectors(c1_metadata, attribute).values())
            c2_vectors += list(calculate_vectors(c2_metadata, attribute).values())
            used_attributes.append(attribute)

    # calculate cosine similarity (equivalent to 1 - cosine distance)
    cosine_similarity = 1 - distance.cosine(c1_vectors, c2_vectors)

    return cosine_similarity, used_attributes, get_vector_headers(used_attributes), c1_vectors, c2_vectors
