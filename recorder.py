import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

class Recorder:
    def __init__(self):
        self.fs = 44100
        self.recording = []
        self.stream = sd.InputStream(callback=self.callback, samplerate=self.fs, channels=2)
        self.is_recording = False

    def start(self):
        self.is_recording = True
        self.recording = []
        self.stream.start()

    def callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording.append(indata.copy())

    def stop(self, filename):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        recording_np = np.concatenate(self.recording)
        write(filename, self.fs, recording_np)  # save as WAV file
        self.stream = sd.InputStream(callback=self.callback, samplerate=self.fs, channels=2)
