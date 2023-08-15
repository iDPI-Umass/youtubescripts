import os
import stat
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
DEFAULT_WHISPER_MODEL = "small"
MAX_SPIDERING_THREADS = 10
PROBABILITY_THRESHOLD = 0.9

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
    "xx": "no language"
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


def collection_init(collection_name):
    if not os.path.exists(os.path.join(ROOT_DIR, "collections")):
        os.makedirs(os.path.join(ROOT_DIR, "collections"))
        try:
            os.chmod(os.path.join(ROOT_DIR, "collections"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        except:
            pass

    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name))
    os.chmod(os.path.join(ROOT_DIR, "collections", collection_name), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "logs"))
    os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "logs"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "metadata"))
    os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "metadata"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts"))
    os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "transcripts"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    os.makedirs(os.path.join(ROOT_DIR, "collections", collection_name, "wavs"))
    os.chmod(os.path.join(ROOT_DIR, "collections", collection_name, "wavs"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
