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

### get_metadata.py
* creates a collection of known YouTube videos from a CSV of video IDs
* output: collection_metadata.csv, .json metadata files, .wav audio files (optional), transcript files (optional)
* requires 1 command line argument: CSV filename

* options:
  * --skipmusicsearch skips searching YouTube Music (resulting metadata CSV will not contain the is_music field)
  * --skipsubtitles skips downloading subtitles created by the uploader
  * --skipautocaptions skips downloading YouTube's automatically generated captions and live chat transcripts
  * --skiplanguage skips downloading audio and using Whisper to classify video language
  * --saveaudio keeps .wav files and saves it to collections/collection_name/wavs

creating a collection:
1. make a CSV of 11-character video IDs, one column, no header
2. copy CSV file to your home folder (/nfs/ang/users/kyzheng/Book1.csv)

`python3 get_metadata.py Book1.csv --skipmusicsearch --skipsubtitles --skipautocaptions --skiplanguage`

### crawl_from_video_id.py
* creates a collection of recommended videos from a given video ID
* depth of 1 creates a collection of ~20 videos, depth of 2 creates a collection of ~400 videos, depth of 3 creates a collection of ~8000 videos
* output: collection_metadata.csv, tree.json, .json metadata files, .wav audio files (optional), transcript files (optional)
* requires 2 command line arguments: starting video ID, tree depth

* options:
  * --skipmusicsearch skips searching YouTube Music (resulting metadata CSV will not contain the is_music field)
  * --skipsubtitles skips downloading subtitles created by the uploader
  * --skipautocaptions skips downloading YouTube's automatically generated captions and live chat transcripts
  * --skiplanguage skips downloading audio and using Whisper to classify video language
  * --saveaudio keeps .wav files and saves it to collections/collection_name/wavs

example: create a collection of recommendations from dQw4w9WgXcQ, and recommendations from those recommendations: 

`python3 crawl_from_video_id.py "dQw4w9WgXcQ" 2`

example: same as above, but skip classifying language and downloading audio (the most time consuming step)

`python3 crawl_from_video_id.py "dQw4w9WgXcQ" 2 --skiplanguage`

### batch_crawl.py
* runs crawl_from_video_id.py over a list of video IDs

* options:
  * --skipmusicsearch skips searching YouTube Music (resulting metadata CSV will not contain the is_music field)
  * --skipsubtitles skips downloading subtitles created by the uploader
  * --skipautocaptions skips downloading YouTube's automatically generated captions and live chat transcripts
  * --skiplanguage skips downloading audio and using Whisper to classify video language
  * --saveaudio keeps .wav files and saves it to collections/collection_name/wavs

creating batches of collections:
1. make a CSV of 11-character video IDs, one column, no header
2. copy CSV files to your home folder on angwin (/nfs/ang/users/kyzheng/batch1.csv)

examples:

`python3 batch_crawl.py batch1.csv`

`python3 batch_crawl.py batch1.csv --skiplanguage`


### personalized_recs.py
* creates personalized recommendation tree from downloaded YouTube html files
* `folder_on_angwin_containing_html_files` should be in a folder in your home folder on angwin

creating a personalized recommended collection:
1. open Chrome and pick an initial YouTube video to start from
2. hold down cmd (Mac) or ctrl (Windows) and click on each recommended video to open in a new background tab
3. starting from the initial video and repeating for each recommendation
   * cmd/ctrl-s to save the page
   * navigate to an appropriate folder on your local machine in the file selector popup
   * select Format: Webpage, Complete
4. after downloading all the webpages, make a folder in your home folder on angwin, move only HTML files over to the new folder

`python3 personalized_recs.py "dQw4w9WgXcQ" "folder_on_angwin_containing_html_files"`

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
* requires at least 2 command line arguments: name of collection1, name of collection2, --[views likes duration comments subscribers year music language]
* NOTE: language predictions with a probability lower than the specified threshold in youtubetools.config are replaced with "xx" (default cutoff is 0.9)

example: compare a random prefix-sampled collection with a 2-depth recommended from "dQw4w9WgXcQ" collection:

`python3 collection_similarity.py "random_prefix_200_20230601_210754_084511" "recs_dQw4w9WgXcQ_2_20230602_100908_183277" --views --likes --duration --comments --subscribers --year --music --language`

```
cosine similarity
0.6506516399387535

compared attributes
['view_count', 'like_count', 'duration', 'comment_count', 'channel_follower_count', 'whisper_lang', 'accessible_in_youtube_music', 'upload_year']

vector bins
[0, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000, 0, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 0, 1, 10, 100, 1000, 10000, 100000, 1000000, 0, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 0, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 'en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr', 'pl', 'ca', 'nl', 'ar', 'sv', 'it', 'id', 'hi', 'fi', 'vi', 'he', 'uk', 'el', 'ms', 'cs', 'ro', 'da', 'hu', 'ta', 'no', 'th', 'ur', 'hr', 'bg', 'lt', 'la', 'mi', 'ml', 'cy', 'sk', 'te', 'fa', 'lv', 'bn', 'sr', 'az', 'sl', 'kn', 'et', 'mk', 'br', 'eu', 'is', 'hy', 'ne', 'mn', 'bs', 'kk', 'sq', 'sw', 'gl', 'mr', 'pa', 'si', 'km', 'sn', 'yo', 'so', 'af', 'oc', 'ka', 'be', 'tg', 'sd', 'gu', 'am', 'yi', 'lo', 'uz', 'fo', 'ht', 'ps', 'tk', 'nn', 'mt', 'sa', 'lb', 'my', 'bo', 'tl', 'mg', 'as', 'tt', 'haw', 'ln', 'ha', 'ba', 'jw', 'su', 'xx', True, False, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

collection 1 vectors
[0.0, 0.0, 0.0, 0.006756756756756757, 0.125, 0.22972972972972974, 0.3783783783783784, 0.24662162162162163, 0.013513513513513514, 0.0, 0.0, 0, 0.0, 0.0033783783783783786, 0.057432432432432436, 0.20270270270270271, 0.34121621621621623, 0.30067567567567566, 0.0945945945945946, 0.0, 0, 0.0, 0.0, 0.0, 0.4797297297297297, 0.4966216216216216, 0.02364864864864865, 0.0, 0, 0.010135135135135136, 0.037162162162162164, 0.16216216216216217, 0.3581081081081081, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.010135135135135136, 0.0472972972972973, 0.04054054054054054, 0.13175675675675674, 0.3614864864864865, 0.32432432432432434, 0.08445945945945946, 0, 0.9527027027027027, 0, 0, 0, 0.0033783783783783786, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.04391891891891892, 1.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.006756756756756757, 0.013513513513513514, 0.0033783783783783786, 0.0033783783783783786, 0.006756756756756757, 0.006756756756756757, 0.0, 0.006756756756756757, 0.0033783783783783786, 0.02702702702702703, 0.04054054054054054, 0.1554054054054054, 0.722972972972973, 0, 0.0033783783783783786]

collection 2 vectors
[0.0, 0.0, 0.004048582995951417, 0.03643724696356275, 0.145748987854251, 0.24696356275303644, 0.2550607287449393, 0.23076923076923078, 0.08097165991902834, 0.0, 0.0, 0, 0.020242914979757085, 0.020242914979757085, 0.12955465587044535, 0.29959514170040485, 0.24696356275303644, 0.21052631578947367, 0.0728744939271255, 0.0, 0, 0.145748987854251, 0.0, 0.0, 0.0, 0.6234817813765182, 0.23076923076923078, 0.0, 0, 0.06882591093117409, 0.145748987854251, 0.21862348178137653, 0.21052631578947367, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.024291497975708502, 0.08502024291497975, 0.2591093117408907, 0.4777327935222672, 0.10526315789473684, 0.04048582995951417, 0.008097165991902834, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 0.8137651821862348, 0.1862348178137652, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.004048582995951417, 0.008097165991902834, 0.0, 0.004048582995951417, 0.004048582995951417, 0.012145748987854251, 0.012145748987854251, 0.05668016194331984, 0.06477732793522267, 0.05668016194331984, 0.7773279352226721, 0, 0.0]
```


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
