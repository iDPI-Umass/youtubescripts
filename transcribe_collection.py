"""
NOTE: forces transcription in korean
"""

import os
import torch
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

max_threads = 10

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-large-v3"


def transcribe(collection, video_id):
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, use_safetensors=True
    )
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        torch_dtype=torch_dtype,
        device=device,
    )
    result = pipe(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"),
                  generate_kwargs={"language": "korean"})
    with open(os.path.join(ROOT_DIR, "collections", collection, "transcripts", f"{video_id}_whisper3.txt"), "w") as f:
        f.write(result['text'])


collection = "metadata_koreanids_20240614_170913_740031"
wav_files = [filename for filename in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "wavs")) if filename.endswith(".wav")]
video_ids = [wav_file.split(".")[0] for wav_file in wav_files]
total_videos = len(wav_files)
pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()


def worker(q):
    while not q.empty():
        video_id = q.get()
        transcribe(collection, video_id)
        pbar.update((total_videos - q.qsize()) / total_videos * 100)
        q.task_done()


q = Queue(maxsize=0)
for video_id in video_ids:
    q.put(video_id)
threads = []
for i in range(max_threads):
    work_thread = Thread(target=worker, args=(q,))
    threads.append(work_thread)
    work_thread.start()
q.join()
