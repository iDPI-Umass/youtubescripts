"""
downloads collection metadata from tree.json files
"""
import os
import argparse
import progressbar
import pandas as pd
from queue import Queue
from threading import Thread
from youtubetools.datadownloader import json_to_csv
from youtubetools.youtubescripts import youtube_tools
from youtubetools.recommendationscraper import flatten_dict

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--saveaudio", action="store_true")
args = parser.parse_args()

metadata_options = {
    "skip_youtube_music_search": args.skipmusicsearch,
    "skip_subtitles": args.skipsubtitles,
    "skip_automatic_captions": args.skipautocaptions
}
download_options = ((not args.skiplanguage or args.saveaudio), True)  # download audio, download metadata

df = pd.read_csv(os.path.join(os.path.expanduser('~'), args.file), header=None)
collections = df[0].tolist()

for collection in collections:
    print(f"{collection} start")
    pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()
    max_threads = 10
    flattened = flatten_dict(collection)
    total_videos = len(list(flattened.keys()))

    def worker(q):
        video_id = q.get()
        youtube_tools(collection, video_id, download_options, metadata_options, args.saveaudio, args.skiplanguage,
                      related_to=flattened[video_id])
        pbar.update((total_videos - q.qsize()) / total_videos * 100)
        q.task_done()

    q = Queue(maxsize=0)
    for video_id in flattened.keys():
        q.put(video_id)
    threads = []
    for i in range(max_threads):
        work_thread = Thread(target=worker, args=(q,))
        threads.append(work_thread)
        work_thread.start()
    q.join()
    json_to_csv(collection)
    print(f"{collection} done")