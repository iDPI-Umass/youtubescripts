"""
functions to download data from YouTube
"""
import os
import json
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error
from youtubetools.datadownloader.audio import download_audio_track
from youtubetools.datadownloader.metadata import download_metadata_transcripts


def download_data(collection: str, video_id: str, download_options=(True, True), metadata_options=None,
                  audio_options=None):
    """
    wrapper function for downloading data (audio, metadata, transcripts) from YouTube
    :param collection: name of collection folder
    :param video_id: 11 character video ID
    :param download_options: (if True download audio, if True download metadata+transcripts)
    :param metadata_options: {"skip_youtube_music_search":True/False, "skip_subtitles":True/False,
                              "skip_automatic_captions":True/False, "skip_metadata_save":True/False}
    :param audio_options: TODO
    :return:
    """
    if metadata_options is None:
        metadata_options = {}
    if audio_options is None:
        audio_options = {}

    assert len(video_id) == 11, "video_id must be 11 characters long"

    # download metadata and transcripts (must download metadata if downloading audio)

    if download_options[1] or download_options[0]:
        try:
            download_metadata_transcripts(collection, video_id, metadata_options)
        except Exception as e:
            log_error(collection, video_id, 'datadownloader.download', str(e))

    # download audio
    if download_options[0]:
        try:
            with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f'{video_id}.json'), 'r',
                      encoding='utf8') as md_file:
                metadata = json.load(md_file)
                # downloading audio from actively live video results in potentially infinite download
                if "is_live" in metadata.keys() and metadata["is_live"]:
                    return
            download_audio_track(collection, video_id, audio_options)
        except Exception as e:
            log_error(collection, video_id, 'datadownloader.download', str(e))
