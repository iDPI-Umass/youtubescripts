"""
runs crawl_from_video_id.py over a list of video IDs
"""
import os
import argparse
import subprocess
import pandas as pd
from queue import Queue

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("layers", type=int)
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
parser.add_argument("--skipmusicsearch", action="store_true")
parser.add_argument("--skipsubtitles", action="store_true")
parser.add_argument("--skipautocaptions", action="store_true")
parser.add_argument("--saveaudio", action="store_true")

args = parser.parse_args()

df = pd.read_csv(os.path.join(os.path.expanduser('~'), args.file), header=None)
root_ids = df[0].tolist()
depth = args.layers

q = Queue(maxsize=0)
for root_id in root_ids:
    q.put(root_id)
while not q.empty():
    root_id = q.get()
    try:
        query = ['python3', 'crawl_from_video_id.py', root_id, str(depth)]
        if args.skiplanguage:
            query.append('--skiplanguage')
        if args.skipmusicsearch:
            query.append('--skipmusicsearch')
        if args.skipsubtitles:
            query.append('--skipsubtitles')
        if args.skipautocaptions:
            query.append('--skipautocaptions')
        if args.saveaudio:
            query.append('--saveaudio')
        subprocess.run(query)
    except Exception as e:
        print(e)
    print(f'{root_id} done')
    q.task_done()
