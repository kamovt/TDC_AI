import numpy as np

class VoiceActivityDetector:
    def __init__(self, threshold=0.04):
        self.threshold = threshold

    def is_speech(self, audio):
        audio = np.asarray(audio, dtype=np.float32)

        # Remove DC offset
        audio = audio - np.mean(audio)

        rms = np.sqrt(np.mean(audio ** 2))

        return rms > self.threshold