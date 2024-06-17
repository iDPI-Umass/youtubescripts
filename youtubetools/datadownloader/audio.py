"""
functions to download audio
"""
import os
import time
import subprocess
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error


def download_audio_track(collection: str, video_id: str, options: dict = None) -> str:
    """
    downloads mono 16khz audio for any YouTube video
    :param collection: name of collection folder
    :param video_id: 11 character video ID
    :param options: TODO
    :return: .wav file address
    """

    # skip downloading if .wav file already exists
    if os.path.isfile(os.path.join(ROOT_DIR, "collections", collection, f"{video_id}.wav")):
        return os.path.join(ROOT_DIR, "collections", collection, f"{video_id}.wav")

    tries = 0
    while tries < 5:
        try:
            query = ['yt-dlp', '-q', '--no-progress', '-o', os.path.join(ROOT_DIR, "collections", collection, "wavs",
                                                                         "%(id)s.%(ext)s"), '-x', '--audio-format',
                     'wav', '--audio-quality', '256K']
            if "twominutes" in options.keys() and options["twominutes"]:
                query += ['--download-sections', '*00:00:00-00:02:00']
            query += ['--ppa', 'ffmpeg:-ar 16000 -ac 1', f'https://www.youtube.com/watch?v={video_id}']

            subprocess.run(query, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav")
        except Exception as e:
            log_error(collection, video_id, "datadownloader_audio", e)
            tries += 1
            time.sleep(5)
    return ""
