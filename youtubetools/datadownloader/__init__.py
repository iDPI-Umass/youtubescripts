"""
provides functions to download+cleanup metadata, audio, and transcripts from YouTube

functions:
json_to_csv: aggregates a collection's metadata json files to a single CSV file
download_data: downloads metadata, transcripts, audio from YouTube
"""
from youtubetools.datadownloader.metadata import json_to_csv
from youtubetools.datadownloader.download import download_data
