import os
import sys
import json
import argparse
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from youtubetools.languageidentifier import identify_language
from youtubetools.datadownloader import download_data, json_to_csv
from youtubetools.recommendationscraper import get_recommendation_tree, flatten_dict


parser = argparse.ArgumentParser()
parser.add_argument("videoid", type=str)
parser.add_argument("layers", type=int)
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
args = parser.parse_args()

max_threads = 10
root_node, depth = args.videoid, args.layers  # "8J-V3J3CBes", 2
collection = get_recommendation_tree(root_node, depth)
flattened = flatten_dict(collection)
total_videos = len(list(flattened.keys()))
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        video_id = q.get()
        if args.skiplanguage:
            download_data(collection, video_id, [False, True])
        else:
            download_data(collection, video_id)
            if os.path.isfile(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav")):
                lang_prediction = identify_language(os.path.join(collection, "wavs", f"{video_id}.wav"))
                with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "r") as md_file:
                    metadata = json.load(md_file)
                metadata["whisper_lang"] = lang_prediction[0]
                metadata["whisper_probability"] = lang_prediction[1]
                with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "w") as md_file:
                    json.dump(metadata, md_file)
                os.remove(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"))
        pbar.update((total_videos-q.qsize())/total_videos*100)
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
