import os
import random
import string
import innertube
import progressbar
from threading import Thread
from datetime import datetime
from youtubetools.logger import log_error
from youtubetools.config import ROOT_DIR, MAX_SPIDERING_THREADS, collection_init


class RandomPrefixSampler:
    def __init__(self, n, collection):
        self.n = n
        self.collection = collection
        self.chars = list(string.ascii_lowercase)
        self.yt_client = innertube.InnerTube("WEB")
        self.prefix_length = 5  # ≥5, otherwise too many results per search and would require continuation token
        self.size_estimate = None
        self.video_ids = []
        self.prefixes = []
        self.pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()])

    def __search(self):
        while len(self.video_ids) < self.n:
            id_prefix = ''.join(random.choice(self.chars) for _ in range(self.prefix_length))
            try:
                search_results = self.yt_client.search(query=f'allinurl:"watch?v={id_prefix}"')
                video_metadata = [a for a in search_results["contents"]["twoColumnSearchResultsRenderer"][
                    "primaryContents"]["sectionListRenderer"]["contents"] if "itemSectionRenderer" in a.keys()][0][
                    "itemSectionRenderer"]["contents"]
                search_video_ids = [video["videoRenderer"]["videoId"] for video in video_metadata if
                                    "videoRenderer" in video.keys()]
                self.video_ids.extend([video_id for video_id in search_video_ids if
                                       self.is_valid_video(video_id, id_prefix)])
                self.prefixes.append(id_prefix)
                self.pbar.update(min(len(self.video_ids) / self.n * 100, 100))
            except Exception as e:
                log_error(self.collection, f"{id_prefix}-XXXXX", "randomsampler_prefixsampling", e)

    def generate(self):
        self.pbar.start()
        threads = []
        for i in range(max(1, min(MAX_SPIDERING_THREADS, self.n / 5))):  # 5 char-length prefix returns ~5 per search
            worker = Thread(target=self.__search)
            threads.append(worker)
            worker.start()
        for thread in threads:
            thread.join()

        self.size_estimate = int((2 ** 64) / (len(self.prefixes) * (2 ** self.prefix_length) *
                                              (64 ** (9 - self.prefix_length)) * 16 / len(self.video_ids)))
        log_error(self.collection, "XXXXXXXXXX", "randomsampler_prefixsampling", self.size_estimate)  # record size
        return self.size_estimate

    def is_valid_video(self, video_id, id_seed):
        if len(video_id) == 11 and video_id.lower().startswith(id_seed.lower()) and video_id[self.prefix_length] == "-":
            return True
        else:
            return False


def get_random_prefix_sample(n=1000):
    collection = f"random_prefix_{n}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    collection_init(collection)
    random_prefix_sampler = RandomPrefixSampler(n, collection)
    random_prefix_sampler.generate()
    with open(os.path.join(ROOT_DIR, "collections", collection, "randomids.txt"), "w") as f:
        f.write('\n'.join(random_prefix_sampler.video_ids) + '\n')
    print(f"size estimate: {random_prefix_sampler.size_estimate}")
    return collection
