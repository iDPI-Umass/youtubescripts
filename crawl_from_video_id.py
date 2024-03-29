"""
creates a collection of recommended videos from a given video ID
"""
import argparse
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.datadownloader import json_to_csv
from youtubetools.youtubescripts import youtube_tools
from youtubetools.recommendationscraper import get_recommendation_tree, flatten_dict


parser = argparse.ArgumentParser()
parser.add_argument("videoid", type=str)
parser.add_argument("layers", type=int)
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--saveaudio", action="store_true")
parser.add_argument("--onlytree", action="store_true")
args = parser.parse_args()

metadata_options = {
    "skip_youtube_music_search": args.skipmusicsearch,
    "skip_subtitles": args.skipsubtitles,
    "skip_automatic_captions": args.skipautocaptions
}
download_options = ((not args.skiplanguage or args.saveaudio), True)  # download audio, download metadata


max_threads = 10
root_node, depth = args.videoid, args.layers  # "8J-V3J3CBes", 2
collection = get_recommendation_tree(root_node, depth)
flattened = flatten_dict(collection)
total_videos = len(list(flattened.keys()))
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        video_id = q.get()
        youtube_tools(collection, video_id, download_options, metadata_options, args.saveaudio, args.skiplanguage,
                      related_to=flattened[video_id])
        pbar.update((total_videos - q.qsize()) / total_videos * 100)
        q.task_done()


if not args.onlytree:
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
