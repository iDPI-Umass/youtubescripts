import os
from config.definitions import ROOT_DIR
from youtubetools.languageidentifier.model_whisper import classify_language_whisper
from youtubetools.languageidentifier.model_voxlingua import classify_language_voxlingua


def identify_language(wav_filepath: str, model_selector: tuple[int, any] = (0, "small")) -> tuple[str, float]:
    """

    :param wav_filepath:
    :param model_selector: (model, model_attribute)
                            model: 0 -> whisper , 1 -> voxlingua107
                            model_attribute: if whisper is selected, then str with model name
                                             if vl107 is selected, then int with chunk length in seconds
    """
    assert len(wav_filepath.split(os.sep)) == 3 and wav_filepath.split(os.sep)[1] == "wavs", \
        "filepath not in testvideoid_20230523_173130/wavs/testvideoid.wav format"
    assert wav_filepath.endswith(".wav"), "filename does not end in .wav"
    assert os.path.isfile(os.path.join(ROOT_DIR, "data", wav_filepath)), "wav file does not exist"

    language, probability = "", 0
    if model_selector[0] == 0:
        language, probability = classify_language_whisper(wav_filepath=wav_filepath, model=model_selector[1])
    if model_selector[0] == 1:
        assert model_selector[1].isdigit(), "chunk length must be integer seconds"
        language, probability = classify_language_voxlingua(wav_filepath=wav_filepath, chunk_seconds=model_selector[1])
    return language, probability
