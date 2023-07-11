# youtubescripts

spidering, language identification, transcription, random prefix sampling, random dialing sampling, cosine similarity between collections

## getting started
1. log into angwin and `ssh bradley`
2. change to mounted storage space: `cd /srv/data/USERNAME`
   *  ensure that you have read, write, and execution permissions in this folder (admin has to set this up)
4. clone repository: `git init` and `git clone https://github.com/iDPI-Umass/youtubescripts.git`
5. change to youtubescripts directory: `cd youtubescripts`
6. install dependencies
   ```
   pip install -r requirements.txt
   ```
   *  (skip if on bradley): if yt-dlp or ffmpeg aren't installed already: 
      ```
      sudo add-apt-repository ppa:tomtomtom/yt-dlp    # Add ppa repo to apt
      sudo apt update                                 # Update package list
      sudo apt install yt-dlp                         # Install yt-dlp
      sudo apt install ffmpeg                         # Install ffmpeg and ffprobe
      ```
6. run crawler script: `python3 crawl_from_video_id.py "dQw4w9WgXcQ" 2`

## sample scripts

### crawl_from_video_id.py
* creates a collection of recommended videos from a given video ID
* detects language of audio with Whisper, searches for video in YouTube Music
* output: metadata.csv, recommendation tree, any available transcripts, metadata JSON files
* requires 2 command line arguments: video ID, tree depth

example: create a collection of recommendations from dQw4w9WgXcQ, and recommendations from those recommendations: 

`python3 crawl_from_video_id.py "dQw4w9WgXcQ" 2`


### personalized_recs.py
* creates recommendation tree from downloaded YouTube html files
* `folder_containing_html_files` should be under the `temp` folder

`python3 personalized_recs.py "dQw4w9WgXcQ" "folder_containing_html_files"`

### prefix_sample.py
* creates a collection of random, prefix-sampled videos
* detects language of audio with Whisper, searches for video in YouTube Music
* output: metadata.csv, list of random IDs, any available transcripts, metadata JSON files
* requires 1 command line argument: minimum random sample size

example: create a collection of 1000 random prefix-sampled YouTube videos

`python3 prefix_sample.py 1000`


### collection_similarity.py
* compares two collections of YouTube videos and returns a cosine similarity value for the calculated vectors
* output: cosine similarity value
* requires 2 command line arguments: name of collection 1, name of collection2

example: compare a random prefix-sampled collection with a 2-depth recommended from "dQw4w9WgXcQ" collection:

`python3 collection_similarity.py "random_prefix_200_20230601_210754_084511" "recs_dQw4w9WgXcQ_2_20230602_100908_183277"`

## file structure
```
└── youtubescripts
    └── collections (data goes here)
        └── testvideoid_20230523_173130 (example collection)
            └── logs (error logs)
                └── 20230524_163654107588_audio_testvideoid.log
            └── metadata
                └── dQw4w9WgXcQ.json
            └── transcripts
                └── dQw4w9WgXcQ.en.vtt
                └── dQw4w9WgXcQ.auto.en-orig.vtt
            └── wavs
                └── dQw4w9WgXcQ.wav
            └── metadata.csv
            └── tree.json
        └── tmp (for storing voxlingua107 model)
    └── temp (put HTML files in a folder here)
        └── folder_containing_html_files
            └── youtube1.html
            └── youtube2.html
            └── youtube3.html
    └── example_script.py
    └── youtubetools
        └── config (package-wide settings)
        └── datadownloader
        └── languageidentifier
        └── randomsampler
        └── recommendationscraper
    └── .gitignore
    └── README.md
    └── requirements.txt
```


## features

### youtube data downloading
`from youtubetools import datadownloader`
* `json_to_csv("testvideoid_20230523_173130")`
  * makes csv of all metadata json files in a given collection
* `download_data("testvideoid_20230523_173130", "dQw4w9WgXcQ")`
  * downloads available metadata, audio file, uploaded captions, and original language auto transcripts
  * searches YouTube Music, adds result to metadata file

### recommendation tree scraping
`from youtubetools import recommendationscraper`
* `get_recommendation_tree("dQw4w9WgXcQ", 3)`
  * creates collection of recommendations, given a root video_id and depth (1≤depth≤6, default is 2)
* `flatten_dict("testvideoid_20230523_173130")`
  * creates dict of unique keys

### language identification
`from youtubetools import languageidentifier`
* [Whisper](youtubetools/languageidentifier/model_whisper.py)
  * `identify_language("testvideoid_20230523_173130/wavs/AAKUqHBuzk4.wav")`
  * uses OpenAI's [Whisper](https://huggingface.co/openai/whisper-large-v2), a pretrained automatic speech recognition and speech translation model
  * language identification implementation from [Joshua Tanner's thread in the Hugging Face Forums](https://discuss.huggingface.co/t/language-detection-with-whisper/26003)
  * choose from 5 different models: `tiny base small medium large-v2`
    * in our tests, large tends to be ~10x slower than tiny
* voxlingua107
  * `identify_language("testvideoid_20230523_173130/wavs/AAKUqHBuzk4.wav", [1])`
  * our original language identification implementation
  * uses SpeechBrain's [VoxLingua107 ECAPA-TDNN model](https://huggingface.co/speechbrain/lang-id-voxlingua107-ecapa)
  * chunks audio into 30 seconds, returns language of chunk with highest probability or language of first chunk with >0.97 confidence 

### random sampling
`from youtubetools import randomsampler`
* random prefix sampling
  * `get_random_prefix_sample(100)`
  * creates collection of random prefix-sampled videos
* random dialing sampling
  * TBA

### local transcription
tba

### metadata analysis
`from youtubetools import analysis`
* cosine similarity
  * `collection_comparison(collection1, collection2)`
