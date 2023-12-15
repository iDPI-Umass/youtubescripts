"""
functions to summarize metadata from random-sampled collections
for use in dashboard
"""
import os
import sys
import json
import math
import stat
import numpy as np
import pandas as pd
from flask import Flask
import matplotlib.pyplot as plt
from datetime import datetime as dt
from youtubetools.config import ROOT_DIR, LANGUAGES


app = Flask(__name__)


class CollectionSummarizer:
    def __init__(self, collection):

        self.__collection = collection
        self.__collection_date, self.__estimated_size, self.__queries, self.__hits, self.__prefix_len, self.__efficiency = self.__load_sample_stats()
        self.__live_videos_count = 0

        self.__metadata = self.__load_metadata()

        self.duration = pd.DataFrame()
        self.duration_labels = []

        self.views = pd.DataFrame()
        self.views_labels = []

        self.likes = pd.DataFrame()
        self.likes_labels = []

        self.comments = pd.DataFrame()
        self.comments_labels = []

        self.subscribers = pd.DataFrame()
        self.subscribers_labels = []

        self.whisper_lang = pd.DataFrame()
        self.whisper_lang_labels = []

        self.upload_date = pd.DataFrame()
        self.annual_uploads = pd.DataFrame()
        self.annual_size = pd.DataFrame()
        self.year_labels = []

        self.live_status = pd.DataFrame()
        self.live_status_labels = []

        self.age_limit = pd.DataFrame()
        self.age_limit_labels = []

        self.availability = pd.DataFrame()
        self.availability_labels = []

        self.music = pd.DataFrame()
        self.music_labels = []

        self.category = pd.DataFrame()
        self.category_labels = []

    def calculate_collection_stats(self, lang_confidence=0.75):
        self.views, self.views_labels = self.__numerical_stats('view_count', 2, [-.01, 0])
        self.likes, self.likes_labels = self.__numerical_stats('like_count', 2, [-.01, 0])
        self.duration, self.duration_labels = self.__numerical_stats('duration', 2)
        self.comments, self.comments_labels = self.__numerical_stats('comment_count', 2, [-.01, 0])
        self.subscribers, self.subscribers_labels = self.__numerical_stats('channel_follower_count', 2, [-.01, 0])

        self.whisper_lang, self.whisper_lang_labels = self.__whisperlang_stats(confidence=lang_confidence)

        self.upload_date, self.annual_uploads, self.annual_size, self.year_labels = self.__uploaddate_stats()

        self.music, self.music_labels = self.__category_stats("accessible_in_youtube_music")
        self.live_status, self.live_status_labels = self.__category_stats("live_status")
        self.age_limit, self.age_limit_labels = self.__category_stats("age_limit")
        self.availability, self.availability_labels = self.__category_stats("availability")
        self.category, self.category_labels = self.__category_stats("categories")

    def export_collection_stats(self):
        collection_stats = {
            "sample": {
                'collection_date': self.__collection_date,
                'size': self.__estimated_size,
                'queries': self.__queries,
                'verified_hits': self.__hits,
                'dead_links': self.__live_videos_count,
                'prefix_len': self.__prefix_len,
                'efficiency': self.__efficiency
            },
            "stats": {
                "fields": [],
                "data": {},
                "quantiles": {}
            }
        }
        if not self.views.empty:
            collection_stats["stats"]["fields"].append("views")
            collection_stats["stats"]["data"]["views"] = {
                "unit": "views",
                "labels": self.views_labels,
                "values": self.views.tolist(),
                "median": self.__metadata["view_count"].median(),
                "mean": self.__metadata["view_count"].mean()
            }
            collection_stats["stats"]["quantiles"]["views"] = self.__calculate_quantiles("view_count")
        if not self.likes.empty:
            collection_stats["stats"]["fields"].append("likes")
            collection_stats["stats"]["data"]["likes"] = {
                "unit": "likes",
                "labels": self.likes_labels,
                "values": self.likes.tolist(),
                "median": self.__metadata["like_count"].median(),
                "mean": self.__metadata["like_count"].mean()
            }
            collection_stats["stats"]["quantiles"]["likes"] = self.__calculate_quantiles("like_count")
        if not self.duration.empty:
            collection_stats["stats"]["fields"].append("duration")
            collection_stats["stats"]["data"]["duration"] = {
                "unit": "seconds",
                "labels": self.duration_labels,
                "values": self.duration.tolist(),
                "median": self.__metadata["duration"].median(),
                "mean": self.__metadata["duration"].mean()
            }
            collection_stats["stats"]["quantiles"]["duration"] = self.__calculate_quantiles("duration")
        if not self.comments.empty:
            collection_stats["stats"]["fields"].append("comments")
            collection_stats["stats"]["data"]["comments"] = {
                "unit": "comments",
                "labels": self.comments_labels,
                "values": self.comments.tolist(),
                "median": self.__metadata["comment_count"].median(),
                "mean": self.__metadata["comment_count"].mean()
            }
            collection_stats["stats"]["quantiles"]["comments"] = self.__calculate_quantiles("comment_count")
        if not self.subscribers.empty:
            collection_stats["stats"]["fields"].append("subscribers")
            collection_stats["stats"]["data"]["subscribers"] = {
                "unit": "subscribers",
                "labels": self.subscribers_labels,
                "values": self.subscribers.tolist(),
                "median": self.__metadata["channel_follower_count"].median(),
                "mean": self.__metadata["channel_follower_count"].mean()
            }
            collection_stats["stats"]["quantiles"]["subscribers"] = self.__calculate_quantiles("channel_follower_count")
        if not self.whisper_lang.empty:
            collection_stats["stats"]["fields"].append("whisper_lang")
            collection_stats["stats"]["data"]["whisper_lang"] = {
                "unit": "language",
                "labels": self.whisper_lang_labels,
                "values": self.whisper_lang.tolist()
            }
        if not self.upload_date.empty:
            collection_stats["stats"]["fields"].append("upload_year")
            collection_stats["stats"]["data"]["upload_year"] = {
                "unit": "year",
                "labels": self.year_labels,
                "values": self.upload_date.tolist(),
                "median": self.__metadata["upload_year"].median(),
                "mean": self.__metadata["upload_year"].mean()
            }
            collection_stats["stats"]["fields"].append("annual_uploads")
            collection_stats["stats"]["data"]["annual_uploads"] = {
                "unit": "year",
                "labels": self.year_labels,
                "values": self.annual_uploads.tolist()
            }
            collection_stats["stats"]["fields"].append("cumulative_uploads")
            collection_stats["stats"]["data"]["cumulative_uploads"] = {
                "unit": "year",
                "labels": self.year_labels,
                "values": self.annual_size.tolist()
            }
            collection_stats["stats"]["quantiles"]["upload_year"] = self.__calculate_quantiles("upload_year")
        if not self.music.empty:
            collection_stats["stats"]["fields"].append("music")
            collection_stats["stats"]["data"]["music"] = {
                "unit": "accessible in YouTube Music",
                "labels": self.music_labels,
                "values": self.music.tolist()
            }
        if not self.live_status.empty:
            collection_stats["stats"]["fields"].append("live_status")
            collection_stats["stats"]["data"]["live_status"] = {
                "unit": "live status",
                "labels": self.live_status_labels,
                "values": self.live_status.tolist()
            }
        if not self.age_limit.empty:
            collection_stats["stats"]["fields"].append("age_limit")
            collection_stats["stats"]["data"]["age_limit"] = {
                "unit": "age limit",
                "labels": self.age_limit_labels,
                "values": self.age_limit.tolist()
            }
        if not self.availability.empty:
            collection_stats["stats"]["fields"].append("availability")
            collection_stats["stats"]["data"]["availability"] = {
                "unit": "availability",
                "labels": self.availability_labels,
                "values": self.availability.tolist()
            }
        if not self.category.empty:
            collection_stats["stats"]["fields"].append("category")
            collection_stats["stats"]["data"]["category"] = {
                "unit": "category",
                "labels": self.category_labels,
                "values": self.category.tolist()
            }


        with open(os.path.join(ROOT_DIR, "summaries", f'{self.__collection}.json'), "w") as f:
            json.dump(collection_stats, f)
        return collection_stats


    def __load_sample_stats(self):
        with open(os.path.join(ROOT_DIR, "collections", self.__collection, "sample_stats.json"), 'r') as f:
            sample_stats = json.load(f)
            return sample_stats["collection_date"], sample_stats["size"], sample_stats["queries"], sample_stats["hits"], sample_stats["prefix_len"], sample_stats["efficiency"]

    def __load_metadata(self):
        metadata_csv = [file for file in os.listdir(os.path.join(ROOT_DIR, "collections", self.__collection)) if
                        file.endswith(".csv")]
        if len(metadata_csv) == 1:
            df = pd.read_csv(os.path.join(ROOT_DIR, "collections", self.__collection, metadata_csv[0]))
            df_live = df[df["channel_id"] == "0"]
            self.__live_videos_count = len(df_live)
            self.__update_size_estimate()
            df = df[df["channel_id"] != "0"]
            df["upload_date"] = pd.to_datetime(df["upload_date"])  # , format="%m/%d/%y")
            df["upload_year"] = df["upload_date"].dt.year
            df = df.replace('',np.nan).fillna(0)
            return df
        else:
            raise Exception("multiple or no CSV files available in collection")

    def __update_size_estimate(self):
        self.__hits -= self.__live_videos_count
        self.__estimated_size = int( (2**64) /
                                     (self.__queries * (2**self.__prefix_len) *
                                      (64 ** (9-self.__prefix_len)) * 16 / self.__hits) )

    def __numerical_stats(self, key, log_base, bin_prepend=[]):
        stop = int(math.log(self.__metadata[key].max(), log_base)) + 1
        bins = bin_prepend + list(np.logspace(start=0, stop=stop, num=stop + 1, base=log_base, dtype='int'))
        distribution = self.__metadata[key].value_counts(normalize=True, sort=False, bins=bins)
        labels = []
        for i in range(1, len(bins)):
            if bins[i] - bins[i - 1] <= 1:
                labels.append(f'{bins[i]:,}')
            else:
                labels.append(f'{(bins[i - 1] + 1):,}-{(bins[i]):,}')
        return distribution, labels

    def __whisperlang_stats(self, confidence=0.6, minimum_frequency=0.005):
        languages = self.__metadata[self.__metadata['whisper_probability'] >= confidence].groupby(
            'whisper_lang', as_index=False)['whisper_lang'].agg({'count': 'count'}).sort_values(
            ['count'], ascending=False, ignore_index=True)
        languages['proportion'] = languages['count'] / len(self.__metadata[self.__metadata['whisper_probability'] >= confidence])
        languages['language_label'] = [LANGUAGES[lang] for lang in languages['whisper_lang'].tolist()]

        low_freq_lang_proportion = languages[languages['proportion'] < minimum_frequency]['proportion'].sum()
        languages = languages.drop(languages[languages['proportion'] < minimum_frequency].index)
        languages = languages.drop("count", axis=1)
        languages.loc[len(languages)] = ["other", low_freq_lang_proportion, "other"]
        # languages.loc[len(languages)] = ["xx", len(self.__metadata[self.__metadata['whisper_probability'] < confidence]) / len(self.__metadata), "no language"]

        return languages['proportion'], languages['language_label'].tolist()

    def __uploaddate_stats(self):
        years = self.__metadata.groupby('upload_year', as_index=False)['upload_year'].agg({'count': 'count'})
        years['proportion'] = years['count'] / years['count'].sum()
        years['estimated_uploads'] = years['proportion'] * self.__estimated_size
        years['estimated_uploads'] = years['estimated_uploads'].astype(int)
        years['estimated_size'] = years['estimated_uploads'].cumsum()
        years['estimated_size'] = years['estimated_size'].astype(int)
        return years['proportion'], years['estimated_uploads'], years['estimated_size'], years['upload_year'].tolist()

    def __category_stats(self, field):
        binned = self.__metadata.groupby(field, as_index=False)[field].agg({'count': 'count'}).sort_values(
            ['count'], ascending=False)
        binned['proportion'] = binned['count'] / binned['count'].sum()
        return binned['proportion'], binned[field].tolist()

    def __calculate_quantiles(self, field):
        q = [i/100 for i in range(1,100)]
        return self.__metadata[field].quantile(q=q, interpolation='higher').tolist()



@app.route('/collections')
def get_collection_dates():
    collections = get_collection_names()
    dates = []
    for i, key in enumerate(collections):
        dates.append({
            "id": i+1,
            "text": key
        })
    return dates



def get_collection_names():
    with open(os.path.join(ROOT_DIR, "summaries", "randomcollections.txt"), "r") as f:
        collections = dict()
        for collection_name in f.readlines():
            name = collection_name.split("_")
            if name[0] == "random" and name[1] == "prefix":
                if os.path.isdir(os.path.join(ROOT_DIR, "collections", collection_name.strip())):
                    collections[name[3]] = collection_name.strip()
    collections = dict(sorted(collections.items(), reverse=True))  # return in newest to oldest order
    return collections


@app.route('/collections/<date>')
def get_collection_stats(collection):
    # collection_names = get_collection_names()
    # if date in collection_names.keys():
    collection_stats = CollectionSummarizer(collection)
    collection_stats.calculate_collection_stats()
    return collection_stats.export_collection_stats()



if not os.path.exists(os.path.join(ROOT_DIR, "summaries")):
    os.makedirs(os.path.join(ROOT_DIR, "summaries"))
    try:
        os.chmod(os.path.join(ROOT_DIR, "summaries"),
                 stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
    except Exception as e:
        print(e)

# folder name
# enter manually
# TODO: get value from log file
# size_estimate = 13430145708
"""

"""

if __name__ == '__main__':
    # collections = [
    #     "random_prefix_25000_20231108_152814_343113",
    #     "random_prefix_20000_20230925_145016_630931",
    #     "random_prefix_25000_20231204_163547_620667"
    # ]
    collections = ["random_prefix_25000_20231212_101404_111559"]
    for collection in collections:
        with open(os.path.join(ROOT_DIR, "summaries", f"{collection}.json"), "w") as f:
            json.dump(get_collection_stats(collection), f)
    # app.run()
# get_collection_stats("20230925")
