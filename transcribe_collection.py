"""
NOTE: forces transcription in korean
"""
import csv
import os
import json
from datetime import datetime

import torch
import progressbar
from queue import Queue
from threading import Thread
from youtubetools.config import ROOT_DIR
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

max_threads = 10

# device = "cuda:0" if torch.cuda.is_available() else "cpu"
# torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# model_id = "openai/whisper-large-v3"


# def transcribe(collection, video_id):
#     model = AutoModelForSpeechSeq2Seq.from_pretrained(
#         model_id, torch_dtype=torch_dtype, use_safetensors=True
#     )
#     model.to(device)
#     processor = AutoProcessor.from_pretrained(model_id)
#     pipe = pipeline(
#         "automatic-speech-recognition",
#         model=model,
#         tokenizer=processor.tokenizer,
#         feature_extractor=processor.feature_extractor,
#         max_new_tokens=128,
#         torch_dtype=torch_dtype,
#         device=device,
#     )
#     """
#     chunk_length_s=30,
#         batch_size=16,
#         return_timestamps=True,
#     """
#     result = pipe(os.path.join(ROOT_DIR, "collections", collection, "wavs", f"{video_id}.wav"),
#                   generate_kwargs={"language": "korean"})
#     with open(os.path.join(ROOT_DIR, "collections", collection, "transcripts", f"{video_id}_whisper3.txt"), "w") as f:
#         f.write(result['text'])


collection = "metadata_koreanids_20240614_170913_740031"


# wav_files = [filename for filename in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "wavs")) if filename.endswith(".wav")]
# video_ids = [wav_file.split(".")[0] for wav_file in wav_files]
# total_videos = len(wav_files)
# pbar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.PercentageLabelBar()]).start()
#
#
# def worker(q):
#     while not q.empty():
#         video_id = q.get()
#         transcribe(collection, video_id)
#         pbar.update((total_videos - q.qsize()) / total_videos * 100)
#         q.task_done()
#
#
# q = Queue(maxsize=0)
# for video_id in video_ids:
#     q.put(video_id)
# threads = []
# for i in range(max_threads):
#     work_thread = Thread(target=worker, args=(q,))
#     threads.append(work_thread)
#     work_thread.start()
# q.join()

all_transcripts = []

transcript_files = [filename for filename in os.listdir(os.path.join(ROOT_DIR, "collections", collection, "transcripts")) if filename.endswith(".txt")]
for transcript_file in transcript_files:
    selected_metadata = {}
    video_id = transcript_file.split("_whisper3.txt")[0]
    with open(os.path.join(ROOT_DIR, "collections", collection, "metadata", f"{video_id}.json"), "r") as f:
        video_metadata = json.load(f)
    selected_metadata["video_id"] = video_id
    selected_metadata["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
    selected_metadata["upload_date"] = datetime.strptime(video_metadata['upload_date'],'%Y%m%d').strftime('%x')
    selected_metadata["view_count"] = video_metadata["view_count"]
    with open(os.path.join(ROOT_DIR, "collections", collection, "transcripts", transcript_file), "r") as f:
        selected_metadata["transcript"] = f.read()
    all_transcripts.append(selected_metadata)

with open(os.path.join(ROOT_DIR, "collections", collection, "transcripts.csv"), "w") as f:
    w = csv.DictWriter(f, all_transcripts[0].keys())
    w.writeheader()
    w.writerows(all_transcripts)


"""
-date
-video ID
-view counts 
-URL
"""
