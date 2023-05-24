import innertube


def __ytm_search(video_id):
    ytm_client = innertube.InnerTube("WEB_REMIX")
    tries = 0
    while tries < 5:
        try:
            search_results = ytm_client.search(query=f"inurl:{video_id}")
            if video_id in str(search_results):
                return True
            else:
                return False
        except Exception as e:
            print(f'ytm_search {video_id} {e}')
            tries += 1


def search_youtube_music(video_id):
    assert len(video_id) == 11, "video_id must be 11 characters long"
    return __ytm_search(video_id)
