import innertube
from youtubetools.logger import log_error


def __ytm_search(collection, video_id):
    ytm_client = innertube.InnerTube("WEB_REMIX")
    tries = 0
    while tries < 5:
        query = f"inurl:{video_id}"
        try:
            search_results = ytm_client.search(query=query)
            search_results_string = str(search_results).replace(query, "")
            if f'https://i.ytimg.com/vi/{video_id}' in search_results_string \
                    or f'https://i.ytimg.com/vi_webp/{video_id}' in search_results_string:
                return True
            # if "No results for " in search_results_string or "Try different keywords" in search_results_string:
            #     return False
            else:
                return False
        except Exception as e:
            log_error(collection, video_id, "datadownloader_youtubemusicsearch", e)
            tries += 1
    return False


def search_youtube_music(collection, video_id):
    assert len(video_id) == 11, "video_id must be 11 characters long"
    return __ytm_search(collection, video_id)
