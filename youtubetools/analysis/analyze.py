import os
import datetime
import pandas as pd
from scipy.spatial import distance
from youtubetools.config import ROOT_DIR, LANGUAGES, PROBABILITY_THRESHOLD

# simple_attributes = ['id', 'title', 'fulltitle', 'thumbnail', 'description', 'average_rating', 'channel_id', 'channel',
#                      'uploader', 'uploader_id', 'availability', 'live_status', 'is_live',
#                      'was_live', 'age_limit', '_has_drm', '_type', 'whisper_probability',
#                     'album', 'artist', 'track', 'release_date', 'release_year']
# other_attributes = ['categories', 'tags', 'automatic_captions', 'subtitles', 'chapters']

bins = {
    'view_count': [0]+[10**a for a in range(11)],  # max 12,000,000,000 views
    'like_count': [0]+[10**a for a in range(8)],  # max 51,000,000 likes
    'duration': [0]+[10**a for a in range(7)],  # max 2,147,400 seconds
    'comment_count': [0]+[10**a for a in range(8)],  # max 19,000,000 comments
    'channel_follower_count': [0]+[10**a for a in range(9)],  # max 243,000,000 subscribers
    'whisper_lang': list(LANGUAGES.keys()),
    'accessible_in_youtube_music': [True, False],
    'upload_year': [year for year in range(2005, int(datetime.date.today().year+1))]
}


def calculate_vectors(metadata, attribute: str) -> dict:
    ordered_binned_vectors = dict.fromkeys(bins[attribute], 0)
    if attribute in ["accessible_in_youtube_music", "whisper_lang"]:
        binned_vectors = metadata[attribute].value_counts(normalize=True).to_dict()
        for bin_label in binned_vectors:
            ordered_binned_vectors[bin_label] = binned_vectors[bin_label]
    else:
        binned_vectors = metadata[attribute].value_counts(bins=bins[attribute], normalize=True).to_dict()
        for bin_label in binned_vectors:
            if isinstance(bin_label, pd._libs.interval.Interval):
                ordered_binned_vectors[int(bin_label.left)] = binned_vectors[bin_label]
    return ordered_binned_vectors


def import_collection_metadata(collection):
    df = pd.read_csv(os.path.join(ROOT_DIR, "collections", collection, "metadata.csv"))
    df['upload_year'] = df['upload_date'].apply(lambda x: int("20"+x[-2:]))
    df.loc[df['whisper_probability'] < PROBABILITY_THRESHOLD, 'whisper_lang'] = 'xx'
    return df


def collection_comparison(c1, c2):
    c1_metadata, c2_metadata = import_collection_metadata(c1), import_collection_metadata(c2)
    # all_attributes = ['view_count', 'like_count', 'duration', 'comment_count', 'channel_follower_count',
    #                   'whisper_lang', 'accessible_in_youtube_music', 'upload_year']
    attributes = ['view_count', 'duration', 'upload_year', 'accessible_in_youtube_music', 'whisper_lang']
    c1_vectors, c2_vectors = [], []
    for attribute in attributes:
        c1_vectors += list(calculate_vectors(c1_metadata, attribute).values())
        c2_vectors += list(calculate_vectors(c2_metadata, attribute).values())
    cosine_similarity = 1 - distance.cosine(c1_vectors, c2_vectors)
    return cosine_similarity, attributes, c1_vectors, c2_vectors
