import os
import torch
import operator
import torchaudio
from typing import Optional, Collection, List, Dict
from config.definitions import ROOT_DIR, DEFAULT_WHISPER_MODEL
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, WhisperForConditionalGeneration, WhisperTokenizer


def __detect_language(model: WhisperForConditionalGeneration, tokenizer: WhisperTokenizer,
                      input_features, possible_languages: Optional[Collection[str]] = None) -> List[Dict[str, float]]:
    # hacky, but all language tokens and only language tokens are 6 characters long
    language_tokens = [t for t in tokenizer.additional_special_tokens if len(t) == 6]
    if possible_languages is not None:
        language_tokens = [t for t in language_tokens if t[2:-2] in possible_languages]
        if len(language_tokens) < len(possible_languages):
            raise RuntimeError(f'Some languages in {possible_languages} did not have associated language tokens')
    language_token_ids = tokenizer.convert_tokens_to_ids(language_tokens)
    # 50258 is the token for transcribing
    logits = model(input_features,
                   decoder_input_ids=torch.tensor([[50258] for _ in range(input_features.shape[0])])).logits
    mask = torch.ones(logits.shape[-1], dtype=torch.bool)
    mask[language_token_ids] = False
    logits[:, :, mask] = -float('inf')
    output_probs = logits.softmax(dim=-1).cpu()
    return [
        {
            lang: output_probs[input_idx, 0, token_id].item()
            for token_id, lang in zip(language_token_ids, language_tokens)
        }
        for input_idx in range(logits.shape[0])
    ]


def classify_language_whisper(wav_filepath: str, model: str = DEFAULT_WHISPER_MODEL) -> tuple[str, float]:
    """
    classify language of wav file using a whisper model
    :param wav_filepath: format testvideoid_20230523_173130/wavs/testvideoid.wav
    :param model: whisper model name (tiny base small medium large-v2)
    :return: language, probability
    """
    assert model in ["tiny", "base", "small", "medium", "large-v2"], \
        "invalid model name (tiny base small medium large-v2)"
    model_name = f'openai/whisper-{model}'
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
    tokenizer = WhisperTokenizer.from_pretrained(model_name)

    waveform, sample_rate = torchaudio.load(os.path.join(ROOT_DIR, "data", wav_filepath))
    input_features = processor(waveform.squeeze().numpy(), sampling_rate=sample_rate,
                               return_tensors="pt").input_features
    language = __detect_language(model, tokenizer, input_features)
    lang_token, probability = sorted(language[0].items(), key=operator.itemgetter(1), reverse=True)[0]
    return lang_token[2:4], round(probability, 4)
