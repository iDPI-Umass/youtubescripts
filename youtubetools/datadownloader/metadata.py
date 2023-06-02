import os
import json
import yt_dlp
import datetime
import pandas as pd
from youtubetools.config import ROOT_DIR
from youtubetools.datadownloader.youtubemusicsearch import search_youtube_music


def __download_metadata(video_id: str):
    ydl_opts = {
        "skip_download": True,
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
            metadata_keys = video_metadata.keys()
            if not bool(options):  # default behavior (search YouTube Music, fetch auto/uploaded transcripts)
                if 'album' in metadata_keys and 'artist' in metadata_keys and 'track' in metadata_keys:
                    video_metadata["accessible_in_youtube_music"] = True
                else:
                    video_metadata["accessible_in_youtube_music"] = search_youtube_music(video_id)
                __download_subtitles(collection, video_id, video_metadata)
                __download_automatic_captions(collection, video_id, video_metadata)
                json.dump(video_metadata, f)
            else:
                if "skip_youtube_music_search" in options.keys() and not options["skip_youtube_music_search"]:
                    if 'album' in metadata_keys and 'artist' in metadata_keys and 'track' in metadata_keys:
                        video_metadata["accessible_in_youtube_music"] = True
                    else:
                        video_metadata["accessible_in_youtube_music"] = search_youtube_music(video_id)
                if "skip_subtitles" in options.keys() and not options["skip_subtitles"]:
                    __download_subtitles(collection, video_id, video_metadata)
                if "skip_automatic_captions" in options.keys() and not options["skip_automatic_captions"]:
                    __download_automatic_captions(collection, video_id, video_metadata)
                if "skip_metadata_save" in options.keys() and not options["skip_metadata_save"]:
                    json.dump(video_metadata, f)


def json_to_csv(collection):
    collection_metadata = []
    simple_attributes = ['id', 'title', 'fulltitle', 'thumbnail', 'description', 'duration', 'view_count',
                         'like_count','average_rating', 'comment_count', 'channel_id', 'channel',
                         'channel_follower_count', 'uploader', 'uploader_id', 'availability', 'live_status', 'is_live',
                         'was_live', 'age_limit', '_has_drm', '_type', 'whisper_lang', 'whisper_probability',
                         'accessible_in_youtube_music', 'album', 'artist', 'track', 'release_date', 'release_year']
    other_attributes = ['categories', 'tags', 'automatic_captions', 'subtitles', 'chapters']

    json_files = [json_file for json_file in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "metadata"))
                  if json_file.endswith(".json")]
    for json_file in json_files:
        video_metadata_dict = {}
        if os.stat(os.path.join(ROOT_DIR, "collections", collection, "metadata", json_file)).st_size == 0:
            video_metadata_dict['id'] = json_file.split('.')[0]
        else:
            with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", json_file), "r") as metadata_file:
                video_metadata = json.load(metadata_file)
            for attribute in simple_attributes:
                if attribute in video_metadata.keys():
                    video_metadata_dict[attribute] = video_metadata[attribute]
                # else:
                #     video_metadata_dict[attribute] = "n/a"
            if 'upload_date' in video_metadata.keys():
                video_metadata_dict['upload_date'] = datetime.datetime.strptime(video_metadata['upload_date'],
                                                                                '%Y%m%d').strftime('%x')
            # else:
            #     video_metadata_dict['upload_date'] = "n/a"
            for attribute in ['categories', 'tags', 'chapters']:
                if attribute in video_metadata.keys():
                    video_metadata_dict[attribute] = json.dumps(video_metadata[attribute])
                # else:
                #     video_metadata_dict[attribute] = "n/a"
            if 'automatic_captions' in video_metadata.keys():
                video_metadata_dict['automatic_captions'] = json.dumps([auto_caption for auto_caption in
                                                            video_metadata['automatic_captions'].keys()
                                                            if auto_caption.endswith("-orig")])
            # else:
            #     video_metadata_dict['automatic_captions'] = "n/a"
            if "subtitles" in video_metadata.keys():
                video_metadata_dict["subtitles"] = json.dumps(list(video_metadata["subtitles"].keys()))
            # else:
            #     video_metadata_dict["subtitles"] = "n/a"
        collection_metadata.append(video_metadata_dict)
    df = pd.DataFrame.from_dict(collection_metadata)
    df.to_csv(os.path.join(ROOT_DIR, "collections", collection, 'metadata.csv'), index=False, header=True)
