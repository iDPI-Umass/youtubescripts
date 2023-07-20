import argparse
import subprocess
import pandas as pd
from queue import Queue

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")

args = parser.parse_args()

file_location = args.file
df = pd.read_csv(file_location, header=None)
root_ids = df[0].tolist()
depth = 2

q = Queue(maxsize=0)
for root_id in root_ids:
    q.put(root_id)
while not q.empty():
    root_id = q.get()
    try:
        query = ['python3', 'crawl_from_video_id.py', f'\"{root_id}\"', depth]
        if args.skiplanguage:
            query.append('--skiplanguage')
        subprocess.run(query)
    except Exception as e:
        print(e)
    q.task_done()