"""
provides helpful variables and functions

functions:
collection_init: sets up folders for a new collection
"""
import os
import stat
import datetime

# root directory is defined as the folder that is two levels up from this file
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))

# sets whisper model size
DEFAULT_WHISPER_MODEL = "large-v3"  # "small"

# limits how many recommendation scraping threads can run at one time
MAX_SPIDERING_THREADS = 10

# whisper language predictions lower than this threshold will be replaced with "xx" in vector calculations
PROBABILITY_THRESHOLD = 0.9

# whisper languages
LANGUAGES = {
    "en": "english",
    "zh": "chinese",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    "ko": "korean",
    "fr": "french",
    "ja": "japanese",
    "pt": "portuguese",
    "tr": "turkish",
    "pl": "polish",
    "ca": "catalan",
    "nl": "dutch",
    "ar": "arabic",
    "sv": "swedish",
    "it": "italian",
    "id": "indonesian",
    "hi": "hindi",
    "fi": "finnish",
    "vi": "vietnamese",
    "he": "hebrew",
    "uk": "ukrainian",
    "el": "greek",
    "ms": "malay",
    "cs": "czech",
    "ro": "romanian",
    "da": "danish",
    "hu": "hungarian",
    "ta": "tamil",
    "no": "norwegian",
    "th": "thai",
    "ur": "urdu",
    "hr": "croatian",
    "bg": "bulgarian",
    "lt": "lithuanian",
    "la": "latin",
    "mi": "maori",
    "ml": "malayalam",
    "cy": "welsh",
    "sk": "slovak",
    "te": "telugu",
    "fa": "persian",
    "lv": "latvian",
    "bn": "bengali",
    "sr": "serbian",
    "az": "azerbaijani",
    "sl": "slovenian",
    "kn": "kannada",
    "et": "estonian",
    "mk": "macedonian",
    "br": "breton",
    "eu": "basque",
    "is": "icelandic",
    "hy": "armenian",
    "ne": "nepali",
    "mn": "mongolian",
    "bs": "bosnian",
    "kk": "kazakh",
    "sq": "albanian",
    "sw": "swahili",
    "gl": "galician",
    "mr": "marathi",
    "pa": "punjabi",
    "si": "sinhala",
    "km": "khmer",
    "sn": "shona",
    "yo": "yoruba",
    "so": "somali",
    "af": "afrikaans",
    "oc": "occitan",
    "ka": "georgian",
    "be": "belarusian",
    "tg": "tajik",
    "sd": "sindhi",
    "gu": "gujarati",
    "am": "amharic",
    "yi": "yiddish",
    "lo": "lao",
    "uz": "uzbek",
    "fo": "faroese",
    "ht": "haitian creole",
    "ps": "pashto",
    "tk": "turkmen",
    "nn": "nynorsk",
    "mt": "maltese",
    "sa": "sanskrit",
    "lb": "luxembourgish",
    "my": "myanmar",
    "bo": "tibetan",
    "tl": "tagalog",
    "mg": "malagasy",
    "as": "assamese",
    "tt": "tatar",
    "haw": "hawaiian",
    "ln": "lingala",
    "ha": "hausa",
    "ba": "bashkir",
    "jw": "javanese",
    "su": "sundanese",
    "xx": "no language",
    "0": "no language"
}
# language code lookup by name, with a few language aliases
TO_LANGUAGE_CODE = {
    **{language: code for code, language in LANGUAGES.items()},
    "burmese": "my",
    "valencian": "ca",
    "flemish": "nl",
    "haitian": "ht",
    "letzeburgesch": "lb",
    "pushto": "ps",
    "panjabi": "pa",
    "moldavian": "ro",
    "moldovan": "ro",
    "sinhalese": "si",
    "castilian": "es",
}

# bins for vector / cosine similarity calculations
BINS = {
    'view_count': [0]+[10**a for a in range(11)],  # max 12,000,000,000 views
    'like_count': [0]+[10**a for a in range(8)],  # max 51,000,000 likes
    'duration': [0]+[10**a for a in range(7)],  # max 2,147,400 seconds
    'comment_count': [0]+[10**a for a in range(8)],  # max 19,000,000 comments
    'channel_follower_count': [0]+[10**a for a in range(9)],  # max 243,000,000 subscribers
    'whisper_lang': list(LANGUAGES.keys()),
    'accessible_in_youtube_music': [True, False],
    'upload_year': [year for year in range(2005, int(datetime.date.today().year+1))]
}


def collection_init(collection_name: str):
    """
    initializes folders for a new collection
    :param collection_name: name of collection to initialize
    """
    if not os.path.exists(os.path.join(ROOT_DIR, "collections")):
        os.makedirs(os.path.join(ROOT_DIR, "collections"))
        try:
            os.chmod(os.path.join(ROOT_DIR, "collections"),
                     stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
        except Exception as e:
            print(e)
    if not os.path.exists(os.path.join(ROOT_DIR, "collections", collection_name)):
        os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name))
        os.chmod(os.path.join(ROOT_DIR, "collections", collection_name),
                 stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if not os.path.exists(os.path.join(ROOT_DIR, "collections", collection_name, "logs")):
        os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "logs"))
        os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "logs"),
                 stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if not os.path.exists(os.path.join(ROOT_DIR, "collections", collection_name, "metadata")):
        os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "metadata"))
        os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "metadata"),
                 stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if not os.path.exists(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts")):
        os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts"))
        os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts"),
                 stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if not os.path.exists(os.path.join(ROOT_DIR, "collections", collection_name, "wavs")):
        os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "wavs"))
        os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "wavs"),
                 stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
