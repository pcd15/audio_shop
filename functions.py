from pvrecorder import PvRecorder
import struct
import whisper
import datetime
import torch
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment
import wave
import contextlib
from sklearn.cluster import AgglomerativeClustering
import numpy as np

#####

def record():
    recorder = PvRecorder(device_index=-1, frame_length=512)
    audio = []
    path = 'audio.wav'
    
    try:
        recorder.start()
        while True:
            frame = recorder.read()
            audio.extend(frame)
    except KeyboardInterrupt:
        recorder.stop()
        with wave.open(path, 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
    finally:
        recorder.delete()

#####

def transcribe(path, num_speakers):
        
    def segment_embedding(segment):
        start = segment["start"]
        end = min(duration, segment["end"])
        clip = Segment(start, end)
        waveform, sample_rate = audio.crop(path, clip)
        return embedding_model(waveform[None])
    
    def time(secs):
        return datetime.timedelta(seconds=round(secs))

    model_size = "large"
    embedding_model = PretrainedSpeakerEmbedding( 
        "speechbrain/spkrec-ecapa-voxceleb",
        device=torch.device("cpu")
    )

    model = whisper.load_model(model_size)
    result = model.transcribe(path)
    segments = result["segments"]
    with contextlib.closing(wave.open(path,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    audio = Audio()
    embeddings = np.zeros(shape=(len(segments), 192))
    for i, segment in enumerate(segments):
        embeddings[i] = segment_embedding(segment)
    embeddings = np.nan_to_num(embeddings)

    clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
    labels = clustering.labels_
    for i in range(len(segments)):
        segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

    f = open("transcript.txt", "w")

    for (i, segment) in enumerate(segments):
        if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
            speaker = segment["speaker"]
            speaker = speaker.replace(" ", "_")
            f.write("\n\n" + speaker + ' ' + str(time(segment["start"])) + '\n')
        f.write(segment["text"][1:] + ' ')
    f.close()

#####

def replace(path, dict):
    with open(path, 'r') as file:
        data = file.read()  

    for key in dict:
        search = key
        replace = dict[key]
        data = data.replace(search, replace)

    with open('transcript_redux.txt', 'w') as file:
        file.write(data)

#####

# record()

# path = "audio.wav"
# num_speakers = 2
# transcribe(path, num_speakers)

# path = 'transcript.txt'
# dict = {"SPEAKER_1": "Macklemore", "SPEAKER_2": "Kesha"}
# replace(path, dict)