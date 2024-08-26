from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
import numpy as np
import librosa
import os
import speech_recognition as sr

app = Flask(__name__)

# Load the trained model
model = load_model('speaker_recognition_model.h5')

# Ensure recordings directory exists
os.makedirs('recordings', exist_ok=True)

# Initialize or load speaker names mapping
speaker_names = {}
if os.path.exists('speaker_names.npy'):
    speaker_names = np.load('speaker_names.npy', allow_pickle=True).item()

def extract_mfcc(filename, n_mfcc=13, duration=5):
    y, sr = librosa.load(filename, duration=duration)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfccs.T, axis=0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_filename = "recordings/temp.wav"
    audio_file.save(temp_filename)

    # Extract MFCC and recognize speaker name
    mfccs = extract_mfcc(temp_filename)
    speaker_name = recognize_speaker_name(temp_filename)

    # Create a directory for the speaker if it doesn't exist
    speaker_dir = os.path.join('recordings', speaker_name)
    os.makedirs(speaker_dir, exist_ok=True)

    # Save the audio file in the speaker's directory
    recording_index = len([f for f in os.listdir(speaker_dir) if f.endswith('.wav')]) + 1
    filename = os.path.join(speaker_dir, f"{recording_index}.wav")
    audio_file.save(filename)

    # Save MFCC features
    mfcc_filename = os.path.join(speaker_dir, f"mfcc_{recording_index}.npy")
    np.save(mfcc_filename, mfccs)

    # Update speaker names mapping
    if speaker_name not in speaker_names.values():
        speaker_id = len(speaker_names)
        speaker_names[speaker_id] = speaker_name
        np.save('speaker_names.npy', speaker_names)

    return jsonify({"message": f"Speaker '{speaker_name}' registered successfully"}), 200

@app.route('/identify', methods=['POST'])
def identify():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files['file']
    filename = "recordings/temp.wav"
    audio_file.save(filename)

    # Extract MFCC and predict speaker
    mfccs = extract_mfcc(filename)
    mfccs = mfccs.reshape(1, -1)
    prediction = model.predict(mfccs)
    speaker_id = np.argmax(prediction)
    speaker_name = speaker_names.get(speaker_id, "Unknown")

    return jsonify({"speaker_name": speaker_name}), 200

def recognize_speaker_name(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text.strip()
    except sr.UnknownValueError:
        return "Unknown"
    except sr.RequestError:
        return "Error"

if __name__ == '__main__':
    app.run(debug=True)









