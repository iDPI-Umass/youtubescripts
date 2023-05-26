import sys
from queue import Queue
from config.definitions import ROOT_DIR
from youtubetools.datadownloader import download_data
from youtubetools.languageidentifier import identify_language
from youtubetools.recommendationscraper import get_recommendation_tree, flatten_dict

collection = get_recommendation_tree(sys.argv[1])
flattened = flatten_dict(collection)

q = Queue(maxsize=0)
for video_id in flattened.keys():
    q.put(video_id)
threads = []


# queue flattened.keys()


# crawl, get tree
# flatten tree -> queue/threaded
#   download audio, metadata, transcripts
#   language_id, insert into metadata file
#   delete audio file
# json to csv
