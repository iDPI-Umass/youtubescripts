import os
import json
import argparse
import subprocess
import progressbar
import pandas as pd
from queue import Queue
from threading import Thread
from datetime import datetime
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error
from youtubetools.config import collection_init
from youtubetools.languageidentifier import identify_language
from youtubetools.datadownloader import download_data, json_to_csv


max_threads = 10
parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")

args = parser.parse_args()
filename = args.file

metadata_options = {
    "skip_youtube_music_search": args.skipmusicsearch,
    "skip_subtitles": args.skipsubtitles,
    "skip_automatic_captions": args.skipautocaptions
}

download_options = [not args.skiplanguage, True]

df = pd.read_csv(os.path.join(os.path.expanduser('~'), filename), header=None)
video_ids = df[0].tolist()
total_videos = len(video_ids)
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()

collection = f"metadata_{filename.split('.csv')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
collection_init(collection)

def worker(q):
    while not q.empty():
        video_id = q.get()
        download_data(collection, video_id, download_options=download_options, metadata_options=metadata_options)
        if not args.skiplanguage:  # language id
            if os.path.isfile(os.path.join(collection, "wavs", f"{video_id}.wav")) and os.path.isfile(
                    os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json")):
                lang_prediction = identify_language(os.path.join(collection, "wavs", f"{video_id}.wav"))
                with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"),
                          "r") as md_file:
                    metadata = json.load(md_file)
                metadata["whisper_lang"] = lang_prediction[0]
                metadata["whisper_probability"] = lang_prediction[1]
                with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"),
                          "w") as md_file:
                    json.dump(metadata, md_file)
                os.remove(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"))
            else:
                log_error(collection, video_id, "get_metadata", f"audio and/or metadata for {video_id} not downloaded")
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
