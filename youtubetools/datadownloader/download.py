from youtubetools.datadownloader.audio import download_audio_track
from youtubetools.datadownloader.metadata import download_metadata
from youtubetools.datadownloader.transcripts import download_transcripts


def download_data(collection, video_id, options = (True, True, True),
                  audio_options = {}, metadata_options = {}, transcripts_options = {}):
    assert len(video_id) == 11, "video_id must be 11 characters long"
    if options[0]:
        download_audio_track(collection, video_id, audio_options)
    if options[1]:
        download_metadata(collection, video_id, metadata_options)
    if options[2]:
        download_transcripts(collection, video_id, transcripts_options)