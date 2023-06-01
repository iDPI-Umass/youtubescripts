import os
import time
import json
import operator
import innertube
from queue import Queue
from functools import reduce
from threading import Thread
from datetime import datetime
from youtubetools.logger import log_error
from youtubetools.config import ROOT_DIR, MAX_SPIDERING_THREADS


class RecommendationScraper:
    def __init__(self, collection, video_id, layers):
        self.yt_client = innertube.InnerTube("WEB")
        self.rec_dict = {}
        self.collection = collection
        self.video_id = video_id
        self.layers = layers

    @staticmethod
    def __get_by_path(recs, path):
        return reduce(operator.getitem, path, recs)

    def __set_by_path(self, recs, path, value):
        self.__get_by_path(recs, path[:-1])[path[-1]] = value

    def __get_recs(self, video_id, max_recs=20):
        tries = 0
        while tries < 5:
            try:
                response = self.yt_client.next(video_id)
                recommendations = \
                    response["contents"]["twoColumnWatchNextResults"]["secondaryResults"]["secondaryResults"]["results"]
                ids = [rec["compactVideoRenderer"]["videoId"] for rec in recommendations if
                       "compactVideoRenderer" in rec.keys() and "videoId" in rec["compactVideoRenderer"].keys()]
                return ids[0:min(max_recs, len(ids))]
            except Exception as e:
                log_error(self.collection, self.video_id, "recommendationscraper", e)
                tries += 1
                time.sleep(5)
        return []

    def __work_thread(self, q):
        while not q.empty():
            path = q.get()
            video_id = path[-1]
            self.__set_by_path(self.rec_dict, path, dict.fromkeys(self.__get_recs(video_id), None))
            q.task_done()

    def __worker_staging(self, path: list, video_ids: list):
        q = Queue(maxsize=0)
        for video_id in video_ids:
            q.put(path + [video_id])
        threads = []
        for i in range(min(len(video_ids), MAX_SPIDERING_THREADS)):
            worker = Thread(target=self.__work_thread, args=(q,))
            threads.append(worker)
            worker.start()
        q.join()

    def bfs(self):
        """
        layer 0 (1):    x
        layer 1 (20):   x                    x                    x                    x                    x
        layer 2 (400):  xxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxx .....
        layer 3 (8,000)
        layer 4 (160,000)
        layer 5 (3,200,000)
        :return:
        """
        if self.layers > 6:
            print("too many layers")
            return None

        if self.layers > 0:
            self.__worker_staging([], [self.video_id])
            if self.layers > 1:
                for key_1 in self.__get_by_path(self.rec_dict, []).keys():
                    path_1 = [key_1]
                    keys_1 = list(self.__get_by_path(self.rec_dict, path_1).keys())
                    self.__worker_staging(path_1, keys_1)
                    if self.layers > 2:
                        for key_2 in keys_1:
                            path_2 = path_1 + [key_2]
                            keys_2 = list(self.__get_by_path(self.rec_dict, path_2).keys())
                            self.__worker_staging(path_2, keys_2)
                            if self.layers > 3:
                                for key_3 in keys_2:
                                    path_3 = path_2 + [key_3]
                                    keys_3 = list(self.__get_by_path(self.rec_dict, path_3).keys())
                                    self.__worker_staging(path_3, keys_3)
                                    if self.layers > 4:
                                        for key_4 in keys_3:
                                            path_4 = path_3 + [key_4]
                                            keys_4 = list(self.__get_by_path(self.rec_dict, path_4).keys())
                                            self.__worker_staging(path_4, keys_4)
                                            if self.layers > 5:
                                                for key_5 in self.__get_by_path(self.rec_dict, path_4).keys():
                                                    path_5 = path_4 + [key_5]
                                                    keys_5 = list(self.__get_by_path(self.rec_dict, path_5).keys())
                                                    self.__worker_staging(path_5, keys_5)
                                                    if self.layers > 6:
                                                        for key_6 in self.__get_by_path(self.rec_dict, path_5).keys():
                                                            path_6 = path_5 + [key_6]
                                                            keys_6 = list(self.__get_by_path(self.rec_dict, path_6).keys())
                                                            self.__worker_staging(path_6, keys_6)
        return self.rec_dict


def get_recommendation_tree(video_id, layers=2):
    collection = f"recs_{video_id}_{layers}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    if not os.path.exists(os.path.join(ROOT_DIR, "collections")):
        os.makedirs(os.path.join(ROOT_DIR, "collections"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection, "logs"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection, "metadata"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection, "transcripts"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection, "wavs"))

    scraper = RecommendationScraper(collection, video_id, layers)
    tree = scraper.bfs()
    with open(os.path.join(ROOT_DIR, "collections", collection, "tree.json"), "w") as file:
        json.dump(tree, file, indent=4)

    return collection


# single threaded recursive implementation (slow!)
# def bfs_recursive(path, layers):
#     # print(path)
#     if layers == 0:
#         return
#     recs = __get_recs(path[-1])
#     __set_by_path(rec_dict, path, dict.fromkeys(recs, None))
#     for rec in recs:
#         bfs_recursive(path+[rec], layers-1)
