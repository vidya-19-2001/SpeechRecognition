import numpy as np
import librosa
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

def extract_mfcc(filename, n_mfcc=13, duration=5):
    y, sr = librosa.load(filename, duration=duration)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfccs.T, axis=0)

# Load recordings and extract features
X = []
y = []
speaker_names = []
base_dir = 'recordings'

for i, speaker in enumerate(os.listdir(base_dir)):
    speaker_names.append(speaker)
    speaker_dir = os.path.join(base_dir, speaker)
    for file in os.listdir(speaker_dir):
        if file.endswith('.wav'):
            mfcc = extract_mfcc(os.path.join(speaker_dir, file))
            X.append(mfcc)
            y.append(i)

X = np.array(X)
y = np.array(y)

# Create a simple neural network model
model = Sequential([
    Dense(256, activation='relu', input_shape=(13,)),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(len(speaker_names), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X, y, epochs=50, batch_size=8)

model.save('speaker_recognition_model.h5')
np.save('speaker_names.npy', speaker_names)

