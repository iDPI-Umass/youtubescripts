from youtubetools.datadownloader.audio import download_audio_track
from youtubetools.datadownloader.metadata import download_metadata_transcripts


def download_data(collection, video_id, download_options=(True, True), audio_options=None, metadata_options=None):
    if metadata_options is None:
        metadata_options = {}
    if audio_options is None:
        audio_options = {}

    assert len(video_id) == 11, "video_id must be 11 characters long"

    if download_options[0]:  # download audio track by default
        download_audio_track(collection, video_id, audio_options)
    if download_options[1]:  # download metadata and transcripts by default
        download_metadata_transcripts(collection, video_id, metadata_options)
