import os
import sys
import json
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error
from youtubetools.languageidentifier import identify_language
from youtubetools.randomsampler import get_random_prefix_sample
from youtubetools.datadownloader import download_data, json_to_csv

max_threads = 10
sample_size = int(sys.argv[1])
collection = get_random_prefix_sample(sample_size)
with open(os.path.join(ROOT_DIR, "collections", collection, "randomids.txt"), "r") as f:
    ids = [random_id[0:11] for random_id in f.readlines()]
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()

def worker(q):
    while not q.empty():
        video_id = q.get()
        download_data(collection, video_id)
        if os.path.isfile(os.path.join(collection, "wavs", f"{video_id}.wav")) and os.path.isfile(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json")):
            lang_prediction = identify_language(os.path.join(collection, "wavs", f"{video_id}.wav"))
            with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "r") as md_file:
                metadata = json.load(md_file)
            metadata["whisper_lang"] = lang_prediction[0]
            metadata["whisper_probability"] = lang_prediction[1]
            with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "w") as md_file:
                json.dump(metadata, md_file)

            os.remove(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"))
        else:
            log_error(collection, video_id, "prefix_sample", f"audio and/or metadata for {video_id} not downloaded")
        pbar.update((len(ids) - q.qsize()) / len(ids) * 100)
        q.task_done()


q = Queue(maxsize=0)
for video_id in ids:
    q.put(video_id)
threads = []
for i in range(max_threads):
    work_thread = Thread(target=worker, args=(q,))
    threads.append(work_thread)
    work_thread.start()
q.join()

json_to_csv(collection)