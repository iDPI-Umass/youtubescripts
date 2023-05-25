import os
import json
import yt_dlp
from config.definitions import ROOT_DIR
from youtubetools.datadownloader.youtubemusicsearch import search_youtube_music


def __download_metadata(video_id: str):
    ydl_opts = {
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.sanitize_info(ydl.extract_info(video_id, download=False))


def __download_subtitles(collection: str, video_id: str, video_metadata: dict) -> list:
    subtitles = list(video_metadata["subtitles"].keys())
    if len(subtitles) > 0:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "writesubtitles": True,
            "subtitleslangs": subtitles,
            "outtmpl": f"{os.path.join(ROOT_DIR, 'collections', collection, 'transcripts')}/%(id)s.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_id])
        return subtitles
    return []


def __download_automatic_captions(collection, video_id, video_metadata: dict, get_english_translation: bool = False):
    automatic_captions = video_metadata["automatic_captions"].keys()
    orig_lang = [lang for lang in automatic_captions if "-orig" in lang]
    if get_english_translation:
        orig_lang += [lang for lang in automatic_captions if lang.lower().startswith("en")]
    if len(orig_lang) > 0:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "writeautomaticsub": True,
            "subtitleslangs": orig_lang,
            "outtmpl": f"{os.path.join(ROOT_DIR, 'collections', collection, 'transcripts')}/%(id)s.auto.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_id])


def download_metadata_transcripts(collection, video_id, options=None):
    if options is None:
        options = {}
    assert os.path.exists(os.path.join(ROOT_DIR, "collections", collection, "metadata")), \
        f"metadata folder for {collection} collection does not exist"

    if f"{video_id}.json" not in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "metadata")):
        with open(f"{os.path.join(ROOT_DIR, 'collections', collection, 'metadata')}/{video_id}.json", "w") as f:
            video_metadata = __download_metadata(video_id)

            if not bool(options):  # default behavior (search YouTube Music, fetch auto/uploaded transcripts)
                video_metadata["accessible_in_youtube_music"] = search_youtube_music(video_id)
                __download_subtitles(collection, video_id, video_metadata)
                __download_automatic_captions(collection, video_id, video_metadata)
                json.dump(video_metadata, f)
            else:
                if "skip_youtube_music_search" in options.keys() and not options["skip_youtube_music_search"]:
                    video_metadata["accessible_in_youtube_music"] = search_youtube_music(video_id)
                if "skip_subtitles" in options.keys() and not options["skip_subtitles"]:
                    __download_subtitles(collection, video_id, video_metadata)
                if "skip_automatic_captions" in options.keys() and not options["skip_automatic_captions"]:
                    __download_automatic_captions(collection, video_id, video_metadata)
                if "skip_metadata_save" in options.keys() and not options["skip_metadata_save"]:
                    json.dump(video_metadata, f)
