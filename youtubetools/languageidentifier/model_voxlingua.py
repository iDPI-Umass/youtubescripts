import os
from youtubetools.config import ROOT_DIR
from speechbrain.pretrained import EncoderClassifier


def __classify_language(wav_file: str, collection: str, chunk_seconds: int) -> tuple[str, float]:
    model = EncoderClassifier.from_hparams(
        source="TalTechNLP/voxlingua107-epaca-tdnn",
        savedir=os.path.join(ROOT_DIR, "collections", "tmp"))  # creates collections/tmp folder
    khz = 16000  # samples per second
    max_confidence_threshold = 0.97  # returns language prediction if confidence is greater than threshold
    save_dir = os.path.join(ROOT_DIR, "collections", collection, "wavs")
    signal = model.load_audio(os.path.join(save_dir, wav_file), save_dir)

    chunk_len = khz * chunk_seconds
    max_confidence = 0
    language_code = ""
    for i in range((len(signal) // chunk_len) + 1):
        start_index = i * chunk_len
        end_index = min(len(signal), start_index + chunk_len)
        if end_index - start_index >= 5 * khz:  # check if duration is greater than 5 seconds
            prediction = model.classify_batch(signal[start_index:end_index])
            if float(prediction[1]) > max_confidence:
                max_confidence = float(prediction[1])
                language_code = prediction[3][0]
                if max_confidence > max_confidence_threshold:
                    return language_code, round(max_confidence, 4)
    return language_code, round(max_confidence, 4)


def classify_language_voxlingua(wav_filepath: str, chunk_seconds: int = 30) -> tuple[str, float]:
    """

    :param chunk_seconds: seconds per chunk, defaults to 30 seconds
    :param wav_filepath: "collection_name/wavs/testvideoid.wav"
    :return: (language_code, confidence)
    """

    filepath = os.path.split(wav_filepath)
    language, probability = __classify_language(wav_file=filepath[1], collection=filepath[0].split(os.sep)[0],
                                                chunk_seconds=chunk_seconds)
    return language, probability
