# youtubescripts

spidering, language identification, transcription, random prefix sampling, random dialing sampling, cosine similarity between collections

## getting started
clone repository: `git init` and `git clone https://github.com/iDPI-Umass/youtubescripts.git`

change to youtubescripts directory: `cd youtubescripts`

install dependencies
```
pip install -r requirements.txt
sudo add-apt-repository ppa:tomtomtom/yt-dlp    # Add ppa repo to apt
sudo apt update                                 # Update package list
sudo apt install yt-dlp                         # Install yt-dlp
sudo apt install ffmpeg                         # Install ffmpeg and ffprobe
```

run crawler script: `python3 crawl_from_video_id.py "dQw4w9WgXcQ" 2`

### file structure
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

### local transcription
tba
### random sampling
tba
#### random prefix sampling
#### random dialing sampling
