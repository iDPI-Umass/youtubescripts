"""
functions to download and process metadata
"""
import os
import json
import yt_dlp
import datetime
import pandas as pd
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error
from youtubetools.datadownloader.youtubemusicsearch import search_youtube_music


def download_metadata(video_id: str) -> dict:
    """
    downloads metadata for a YouTube video
    :param video_id: 11 character video ID
    :return: metadata dict
    """
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "noprogress": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.sanitize_info(ydl.extract_info(video_id, download=False))


def __download_subtitles(collection: str, video_id: str, video_metadata: dict) -> list:
    """
    downloads user-uploaded subtitle files for a YouTube video
    :param collection: name of collection folder
    :param video_id: 11 character video ID
    :param video_metadata: metadata dict
    :return: list of subtitles downloaded
    """
    subtitles = list(video_metadata["subtitles"].keys())
    if len(subtitles) > 0:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "noprogress": True,
            "writesubtitles": True,
            "subtitleslangs": subtitles,
            "outtmpl": f"{os.path.join(ROOT_DIR, 'collections', collection, 'transcripts')}/%(id)s.%(ext)s"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_id])
            return subtitles
        except Exception as e:
            log_error(collection, video_id, "download_subtitles", str(e))
    return []


def __download_automatic_captions(collection: str, video_id: str, video_metadata: dict,
                                  get_english_translation: bool = False) -> None:
    """
    downloads auto-generated caption files and live chat logs for a YouTube video
    :param collection: name of collection folder
    :param video_id: 11 characer video ID
    :param video_metadata: metadata dict
    :param get_english_translation: flag to download english translation of auto caption, if available
    :return: None
    """
    automatic_captions = video_metadata["automatic_captions"].keys()

    # caption files that have "-orig" are in the language identified by YouTube
    orig_lang = [lang for lang in automatic_captions if "-orig" in lang]

    # optional: download english translation of original language, if available
    if get_english_translation:
        orig_lang += [lang for lang in automatic_captions if lang.lower().startswith("en")]

    if len(orig_lang) > 0:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "noprogress": True,
            "writeautomaticsub": True,
            "subtitleslangs": orig_lang,
            "outtmpl": f"{os.path.join(ROOT_DIR, 'collections', collection, 'transcripts')}/%(id)s.auto.%(ext)s"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_id])
        except Exception as e:
            log_error(collection, video_id, "download_automatic_captions", str(e))


def download_metadata_transcripts(collection: str, video_id: str, options: dict = None) -> None:
    """
    consolidated function for downloading metadata and transcripts
    :param collection: name of collection folder
    :param video_id: 11 character video ID
    :param options: dict of download options
    :return: None
    """
    if options is None:
        options = {}
    assert os.path.exists(os.path.join(ROOT_DIR, "collections", collection, "metadata")), \
        f"metadata folder for {collection} collection does not exist"

    if f"{video_id}.json" not in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "metadata")):
        with open(f"{os.path.join(ROOT_DIR, 'collections', collection, 'metadata')}/{video_id}.json", "w",
                  encoding='utf8') as f:
            try:
                video_metadata = download_metadata(video_id)
            except Exception as e:
                video_metadata = {}
                log_error(collection, video_id, "datadownloader_metadata_metadata", e)
            metadata_keys = video_metadata.keys()
            if not bool(options):  # default behavior (search YouTube Music, fetch auto/uploaded transcripts)
                # search YouTube Music
                if 'album' in metadata_keys and 'artist' in metadata_keys and 'track' in metadata_keys:
                    video_metadata["accessible_in_youtube_music"] = True
                else:
                    video_metadata["accessible_in_youtube_music"] = search_youtube_music(collection, video_id)

                # download transcripts
                if "is_live" in video_metadata.keys() and video_metadata["is_live"]:
                    # subtitle download goes forever if video is live while trying to download subtitles
                    pass
                else:
                    try:
                        __download_subtitles(collection, video_id, video_metadata)
                        __download_automatic_captions(collection, video_id, video_metadata)
                    except Exception as e:
                        log_error(collection, video_id, "datadownloader_metadata_subtitles", e)

                json.dump(video_metadata, f, indent=4, ensure_ascii=False)
            else:
                if "skip_youtube_music_search" in options.keys() and not options["skip_youtube_music_search"]:
                    if 'album' in metadata_keys and 'artist' in metadata_keys and 'track' in metadata_keys:
                        video_metadata["accessible_in_youtube_music"] = True
                    else:
                        video_metadata["accessible_in_youtube_music"] = search_youtube_music(collection, video_id)
                if "skip_subtitles" in options.keys() and not options["skip_subtitles"]:
                    __download_subtitles(collection, video_id, video_metadata)
                if "skip_automatic_captions" in options.keys() and not options["skip_automatic_captions"]:
                    __download_automatic_captions(collection, video_id, video_metadata)
                if "skip_metadata_save" not in options.keys():
                    json.dump(video_metadata, f, indent=4, ensure_ascii=False)
                if "skip_metadata_save" in options.keys() and not options["skip_metadata_save"]:
                    json.dump(video_metadata, f, indent=4, ensure_ascii=False)


def json_to_csv(collection: str, skip_attributes: list[str] = None) -> None:
    """
    consolidates metadata JSON files into a single CSV file for a collection
    :param collection: name of collection folder
    :return: None
    """
    if skip_attributes is None:
        skip_attributes = []

    collection_metadata = []
    simple_attributes = ['title', 'fulltitle', 'thumbnail', 'description', 'duration', 'view_count',
                         'like_count', 'average_rating', 'comment_count', 'channel_id', 'channel',
                         'channel_follower_count', 'uploader', 'uploader_id', 'availability', 'live_status', 'is_live',
                         'was_live', 'age_limit', '_has_drm', '_type', 'whisper_lang', 'whisper_probability',
                         'accessible_in_youtube_music', 'related_to']
    ytmusic_attributes = ['album', 'artist', 'track', 'release_date', 'release_year']
    other_attributes = ['categories', 'tags', 'automatic_captions', 'subtitles', 'chapters']

    json_files = [json_file for json_file in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "metadata"))
                  if json_file.endswith(".json")]
    for json_file in json_files:
        video_metadata_dict = {}
        if os.stat(os.path.join(ROOT_DIR, "collections", collection, "metadata", json_file)).st_size == 0:
            video_metadata_dict['id'] = json_file.split('.')[0]
        else:
            try:
                with (open(os.path.join(ROOT_DIR, "collections", collection, "metadata", json_file), "r", encoding='utf8')
                      as metadata_file):
                    video_metadata = json.load(metadata_file)
                video_metadata_dict['id'] = json_file.split('.')[0]
                for attribute in simple_attributes:
                    if attribute in video_metadata.keys() and attribute not in skip_attributes:
                        video_metadata_dict[attribute] = video_metadata[attribute]
                    else:
                        video_metadata_dict[attribute] = 0
                for attribute in ytmusic_attributes:
                    if attribute in video_metadata.keys() and attribute not in skip_attributes:
                        video_metadata_dict[attribute] = video_metadata[attribute]

                if 'upload_date' in video_metadata.keys():
                    video_metadata_dict['upload_date'] = datetime.datetime.strptime(video_metadata['upload_date'],
                                                                                    '%Y%m%d').strftime('%x')
                if 'categories' in video_metadata.keys():
                    if video_metadata['categories'] is not None:
                        video_metadata_dict['categories'] = video_metadata['categories'][0]
                    else:
                        video_metadata_dict['categories'] = None
                for attribute in ['tags', 'chapters', 'related_to']:
                    if attribute in video_metadata.keys() and attribute not in skip_attributes:
                        video_metadata_dict[attribute] = json.dumps(video_metadata[attribute])
                if 'automatic_captions' in video_metadata.keys():
                    video_metadata_dict['automatic_captions'] = json.dumps([auto_caption for auto_caption in
                                                                            video_metadata['automatic_captions'].keys()
                                                                            if auto_caption.endswith("-orig")])
                if "subtitles" in video_metadata.keys():
                    video_metadata_dict["subtitles"] = json.dumps(list(video_metadata["subtitles"].keys()))
            except Exception as e:
                print(json_file.split('.')[0])
                log_error(collection, json_file.split('.')[0], "datadownloader_metadata_jsontocsv", e)
        collection_metadata.append(video_metadata_dict)
    df = pd.DataFrame.from_dict(collection_metadata)
    df.to_csv(os.path.join(ROOT_DIR, "collections", collection, 'collection_metadata.csv'), index=False, header=True)
