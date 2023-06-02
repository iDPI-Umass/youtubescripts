import os
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
DEFAULT_WHISPER_MODEL = "small"
MAX_SPIDERING_THREADS = 10


def collection_init(collection_name):
    if not os.path.exists(os.path.join(ROOT_DIR, "collections")):
        os.makedirs(os.path.join(ROOT_DIR, "collections"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "logs"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "metadata"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts"))
    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "wavs"))
