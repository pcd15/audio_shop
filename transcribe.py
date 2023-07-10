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

def segment_embedding(segment):
    start = segment["start"]
    end = min(duration, segment["end"])
    clip = Segment(start, end)
    waveform, sample_rate = audio.crop(path, clip)
    return embedding_model(waveform[None])

def time(secs):
    return datetime.timedelta(seconds=round(secs))

path = "audio.wav"
model_size = "large"
num_speakers = 2
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

f = open("trans.txt", "w")

# for (i, segment) in enumerate(segments):
#     if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
#         speaker = segment["speaker"]
#         speaker = speaker.replace(" ", "_")
#         f.write("\n\n" + speaker + ' ' + str(time(segment["start"])) + '\n')
#     f.write(segment["text"][1:] + ' ')
# f.close()

for (i, segment) in enumerate(segments):
    if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
        speaker = segment["speaker"]
        speaker = speaker.replace(" ", "_")
        f.write("\n" + speaker + ' ' + str(time(segment["start"])) + '\n')
    f.write(segment["text"][1:] + ' ')
f.close()