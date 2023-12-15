"""
creates a collection of recommended videos from a given video ID
"""
import os
import json
import argparse
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from youtubetools.datadownloader import json_to_csv
from youtubetools.datadownloader.metadata import download_metadata


parser = argparse.ArgumentParser()
parser.add_argument("collection", type=str)
args = parser.parse_args()



max_threads = 10
json_files = [json_file for json_file in os.listdir(os.path.join(ROOT_DIR, "collections", args.collection, "metadata")) if json_file.endswith(".json")]
total_videos = len(json_files)
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        json_file = q.get()
        video_id = json_file.split(".")[0]
        downloaded_metadata = {}
        try:
            with open(os.path.join(ROOT_DIR, "collections", args.collection, "metadata", json_file), "r") as f:
                downloaded_metadata = json.load(f)
            new_metadata = download_metadata(video_id)
            like_count = new_metadata["like_count"]
            if like_count is None:
                like_count = 0
            downloaded_metadata["like_count"] = like_count
            # print(f'{video_id} {downloaded_metadata["like_count"]}')
        except Exception as e:
            print(f'{video_id} {e}')
            downloaded_metadata["like_count"] = 0
        with open(os.path.join(ROOT_DIR, "collections", args.collection, "metadata", json_file), "w") as f:
            json.dump(downloaded_metadata, f)
        pbar.update((total_videos - q.qsize()) / total_videos * 100)
        q.task_done()


q = Queue(maxsize=0)
for json_file in json_files:
    q.put(json_file)
threads = []
for i in range(max_threads):
    work_thread = Thread(target=worker, args=(q,))
    threads.append(work_thread)
    work_thread.start()
q.join()

# json_to_csv(args.collection)
