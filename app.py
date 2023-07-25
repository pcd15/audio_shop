from flask import Flask, render_template, send_file, request, redirect
from werkzeug.utils import secure_filename
from functions import transcribe, other_transcribe, replace
from pvrecorder import PvRecorder
from threading import Thread
import whisper
import struct
import wave
import os

UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'wav', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

audio = []
flag = True
not_started = True
num_speakers = 1

def record():
    global audio
    global flag
    recorder = PvRecorder(device_index=-1, frame_length=512)
    recorder.start()
    while flag:    
        frame = recorder.read()
        audio.extend(frame)
    recorder.stop()
    recorder.delete()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html', num_speakers="")

@app.route('/start', methods=('GET','POST'))
def start():
    global not_started
    if not_started:
        not_started = False
        thread = Thread(target=record)
        thread.start()
    return render_template('index.html', num_speakers="")

@app.route('/stop', methods=('GET','POST'))
def stop():
    global audio
    global flag
    global not_started
    if not not_started:
        flag = False
        path = 'audio.wav'
        with wave.open(path, 'w') as file:
            file.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            file.writeframes(struct.pack("h" * len(audio), *audio))
        flag = True
        not_started = True
        audio = []
        return send_file(path, as_attachment=True)
    return render_template('index.html', num_speakers="")

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    global num_speakers
    if request.method == 'POST':
        num_speakers = (int) (request.form['number'])
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            model = whisper.load_model("large")
            try:
                transcribe(model, path, num_speakers)
            except ValueError:
                other_transcribe(model, path)
            os.remove(path)
            try:
                os.remove("audio.wav")
            except OSError:
                pass
            return send_file('transcript.txt', as_attachment=True)
    return redirect(request.url)

@app.route('/get_speakers', methods=['GET', 'POST'])
def get_speakers():
    global num_speakers
    if request.method == 'POST':
        num_speakers = (int) (request.form['number'])
        return render_template('index.html', num_speakers=num_speakers)
    return redirect(request.url)

@app.route('/update', methods=['GET', 'POST'])
def update():
        global num_speakers
        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                dict = {}
                for num in range(1, num_speakers + 1):
                    key = 'SPEAKER_' + str(num)
                    value = request.form[str(num)]
                    dict[key] = value
                replace(path, dict)
                os.remove(path)
                try:
                    os.remove("transcript.txt")
                except OSError:
                    pass
                return send_file('transcript_redux.txt', as_attachment=True)
        return redirect(request.url)

if __name__=='__main__':
    app.run(debug=True)

# to reset chrome: chrome://net-internals/#sockets