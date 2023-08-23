import os
import argparse
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from youtubetools.datadownloader import json_to_csv
from youtubetools.youtubescripts import youtube_tools
from youtubetools.randomsampler import get_random_prefix_sample

max_threads = 10
parser = argparse.ArgumentParser()
parser.add_argument("size", type=int, help="folder in your angwin home folder")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
parser.add_argument("--saveaudio", action="store_true")

args = parser.parse_args()
metadata_options = {
    "skip_youtube_music_search": args.skipmusicsearch,
    "skip_subtitles": args.skipsubtitles,
    "skip_automatic_captions": args.skipautocaptions
}
download_options = ((not args.skiplanguage or args.saveaudio), True)  # download audio, download metadata

sample_size = args.size
collection = get_random_prefix_sample(sample_size)
with open(os.path.join(ROOT_DIR, "collections", collection, "randomids.txt"), "r") as f:
    ids = [random_id[0:11] for random_id in f.readlines()]
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        video_id = q.get()
        youtube_tools(collection, video_id, download_options, metadata_options, args.saveaudio, args.skiplanguage)
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