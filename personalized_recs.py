"""
creates personalized recommendation tree from downloaded YouTube html files
"""
import argparse
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.youtubescripts import youtube_tools
from youtubetools.datadownloader import json_to_csv
from youtubetools.recommendationscraper import flatten_dict, create_personalized_rec_collection

max_threads = 10
parser = argparse.ArgumentParser()
parser.add_argument("rootid", type=str, help="11 character ID of starting video")
parser.add_argument("folder", type=str, help="folder in your angwin home folder")
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

root_node, folder_on_angwin = args.rootid, args.folder  # "8J-V3J3CBes", "loginrectest"
collection = create_personalized_rec_collection(folder_on_angwin, root_node)
flattened = flatten_dict(collection)
total_videos = len(list(flattened.keys()))
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        video_id = q.get()
        youtube_tools(collection, video_id, download_options, metadata_options,
                      args.saveaudio, args.skiplanguage, flattened[video_id])
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
