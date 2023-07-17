import argparse
import subprocess
from queue import Queue

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file location of csv")
parser.add_argument("--skiplanguage", action="store_true", help="if true, skips language detection")
args = parser.parse_args()
print(args.file)
print(args.skiplanguage)

depth = 2
root_ids = []

q = Queue(maxsize=0)
for root_id in root_ids:
    q.put(root_id)
while not q.empty():
    root_id = q.get()
    try:
        subprocess.run(['python3', 'crawl_from_video_id.py', f'\"{root_id}\"'], depth)
    except Exception as e:
        print(e)