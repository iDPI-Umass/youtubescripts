import os
import json
import yt_dlp
from config.definitions import ROOT_DIR
from youtubetools.datadownloader.youtubemusicsearch import search_youtube_music


def download_metadata(collection, video_id):
    assert os.path.exists(os.path.join(ROOT_DIR, "collections", collection, "metadata")), \
        f"metadata folder for {collection} collection does not exist"

    if f"{video_id}.json" not in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "metadata")):
        ydl_opts = {
            "quiet": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with open(f"{os.path.join(ROOT_DIR, 'collections', collection, 'metadata')}/{video_id}.json", "w") as f:
                video_metadata = ydl.sanitize_info(ydl.extract_info(video_id, download=False))
                video_metadata["accessible_in_youtube_music"] = search_youtube_music(video_id)
                json.dump(video_metadata, f)
