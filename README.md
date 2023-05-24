# youtubescripts

spidering, language identification, transcription, random prefix sampling, random dialing sampling

## language identification
`from youtubetools.languageidentifier import identify_language`

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


