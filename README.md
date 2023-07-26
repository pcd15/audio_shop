# The One-Stop Audio Shop
###### By Paul Dilly | In collaboration with [Energy Hardware](https://energyhardware.com/)

Built upon Python's Flask framework, this project enables you to record and transcribe audio with only a few clicks—a perfect solution to the hassle of note-taking during meetings and lectures.

## Setup
* Clone this repository into your IDE of choice.
* Install all dependencies by running ```pip install -r requirements.txt``` in the terminal.
* Simply start the app with the ```flask run``` command, and you're ready to go!

## Steps
* Record audio, then download the resulting .wav file. You can skip this step if you already have an audio file you'd like to transcribe.
* Upload a .wav file to be transcribed--this can take a few minutes--then download the resulting .txt file.
* If you'd like to replace the speaker tags that come with the transcribed file, you can upload the file, along with the new names for each speaker, to replace the tags with the corresponding names you inputted.

**Side Note:** If the audio you've transcribed in the above step doesn't contain speaker tags, it's because your file wasn't able to undergo the speaker-diarization process. To correct this, try recording a longer portion of audio and/or including more than one speaker in your file.

## Resources
* Transcription: The code this project uses to transcribe audio was adapted from this [resource](https://colab.research.google.com/drive/1V-Bt5Hm2kjaDb4P1RyMSswsDKyrzc2-3?usp=sharing) published by Dwarkesh Patel.
* CSS: The speech bubbles featured on this project's webpage were inspired by this [blog post](https://auralinna.blog/post/2017/how-to-make-a-css-speech-bubble-with-borders-and-drop-shadow) by Tero Auralinna.