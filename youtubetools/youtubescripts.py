import os
import json
from youtubetools.config import ROOT_DIR
from youtubetools.logger import log_error
from youtubetools.datadownloader import download_data


def youtube_tools(
        collection: str,
        video_id: str,
        download_options: tuple[bool, bool],
        metadata_options: dict,
        save_audio: bool,
        skip_language: bool,
        related_to: list[str] = None,
        audio_options: dict = None):
    download_data(collection, video_id, download_options, metadata_options, audio_options)

    if related_to is not None:
        with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "r",
                  encoding='utf8') as md_file:
            metadata = json.load(md_file)
            metadata["related_to"] = related_to
        with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "w", encoding='utf8') as md_file:
            json.dump(metadata, md_file, indent=4, ensure_ascii=False)

    if not skip_language:
        if (os.path.isfile(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav")) and
                os.path.isfile(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"))):
            with (open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "r",
                       encoding='utf8') as md_file):
                metadata = json.load(md_file)
            if "whisper_lang" not in metadata.keys():
                from youtubetools import identify_language
                lang_prediction = identify_language(os.path.join(collection, "wavs", f"{video_id}.wav"))

                metadata["whisper_lang"] = lang_prediction[0]
                metadata["whisper_probability"] = lang_prediction[1]
                with (open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "w",
                           encoding='utf8') as md_file):
                    json.dump(metadata, md_file, indent=4, ensure_ascii=False)
            if not save_audio:
                os.remove(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"))
        else:
            log_error(collection, video_id, "get_metadata", f"audio and/or metadata for {video_id} not downloaded")
