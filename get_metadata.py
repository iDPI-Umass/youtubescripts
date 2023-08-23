import os
import argparse
import progressbar
import pandas as pd
from queue import Queue
from threading import Thread
from datetime import datetime
from youtubetools.config import collection_init
from youtubetools.datadownloader import json_to_csv
from youtubetools.youtubescripts import youtube_tools

# import json
# from youtubetools.config import ROOT_DIR
# from youtubetools.logger import log_error
# from youtubetools.languageidentifier import identify_language
# from youtubetools.datadownloader import download_data, json_to_csv


max_threads = 10
parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
parser.add_argument("--saveaudio", action="store_true")

args = parser.parse_args()
filename = args.file

metadata_options = {
    "skip_youtube_music_search": args.skipmusicsearch,
    "skip_subtitles": args.skipsubtitles,
    "skip_automatic_captions": args.skipautocaptions
}

download_options = ((not args.skiplanguage or args.saveaudio), True)  # download audio, download metadata

df = pd.read_csv(os.path.join(os.path.expanduser('~'), filename), header=None)
video_ids = df[0].tolist()
total_videos = len(video_ids)
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()

collection = f"metadata_{filename.split('.csv')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
collection_init(collection)


def worker(q):
    while not q.empty():
        video_id = q.get()
        youtube_tools(collection, video_id, download_options, metadata_options, args.saveaudio, args.skiplanguage)
        pbar.update((total_videos - q.qsize()) / total_videos * 100)
        q.task_done()


q = Queue(maxsize=0)
for video_id in video_ids:
    q.put(video_id)
threads = []
for i in range(max_threads):
    work_thread = Thread(target=worker, args=(q,))
    threads.append(work_thread)
    work_thread.start()
q.join()

json_to_csv(collection)
