import os
from youtubetools.config import ROOT_DIR, DEFAULT_WHISPER_MODEL


def identify_language(wav_filepath: str, model_selector: list = (0, DEFAULT_WHISPER_MODEL)) -> tuple[str, float]:
    """

    :param wav_filepath:
    :param model_selector: (model) or (model, model_attribute)

                           model: 0 -> whisper , 1 -> voxlingua107

                           optional:
                           model_attribute: if whisper is selected, then str with model name (small default)
                                            if vl107 is selected, then int with chunk length in seconds (30 default)
    """
    assert 1 <= len(model_selector) < 3, "model_selector must have 1 or 2 arguments"
    assert len(wav_filepath.split(os.sep)) == 3 and wav_filepath.split(os.sep)[1] == "wavs", \
        "filepath not in testvideoid_20230523_173130/wavs/testvideoid.wav format"
    assert wav_filepath.endswith(".wav"), "filename does not end in .wav"
    assert os.path.isfile(os.path.join(ROOT_DIR, "collections", wav_filepath)), "wav file does not exist"

    language, probability = "", 0

    if model_selector[0] == 0:  # whisper model
        from youtubetools.languageidentifier.model_whisper import classify_language_whisper
        if len(model_selector) == 1:
            language, probability = classify_language_whisper(wav_filepath)
        elif len(model_selector) == 2:
            language, probability = classify_language_whisper(wav_filepath=wav_filepath, model=model_selector[1])

    elif model_selector[0] == 1:  # voxlingua107 model
        from youtubetools.languageidentifier.model_voxlingua import classify_language_voxlingua
        if len(model_selector) == 1:
            language, probability = classify_language_voxlingua(wav_filepath)
        elif len(model_selector) == 2:
            language, probability = classify_language_voxlingua(wav_filepath=wav_filepath,
                                                                chunk_seconds=model_selector[1])
    return language, probability
