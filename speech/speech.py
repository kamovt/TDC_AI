import time
from collections import deque

import numpy as np
import sounddevice as sd

from .vad import VoiceActivityDetector
from .whisper import Whisper
from .audio_state import TTS_PLAYING

class SpeechRecognizer:

    SAMPLE_RATE = 16000
    CHANNELS = 1

    CHUNK_MS = 30

    CHUNK_SIZE = int(
        SAMPLE_RATE * CHUNK_MS / 1000
    )

    PRE_BUFFER_SECONDS = 0.5

    SILENCE_SECONDS = 2.5

    def __init__(self):

        self.whisper = Whisper()

        self.vad = VoiceActivityDetector()

        self.pre_buffer = deque(
            maxlen=int(
                self.PRE_BUFFER_SECONDS
                * self.SAMPLE_RATE
            )
        )

    def transcribe_audio(self, audio):

        print("Transcribing...")

        text = self.whisper.transcribe(
            audio
        )

        return text

    def process_audio(self, audio):

        print("Processing audio...")

        if audio is None or len(audio) == 0:
            return None

        audio = np.asarray(
            audio,
            dtype=np.float32
        ).flatten()

        return self.transcribe_audio(audio)

    def get_default_input_device(self):

        device_id = sd.default.device[0]

        info = sd.query_devices(device_id)

        print(f"Using microphone: {info['name']}")

        return device_id

    def listen(self):

        print("Listening...")

        # Never carry audio from a previous recording.
        self.pre_buffer.clear()

        recording = []
        recording_started = False

        silence_start = None
        ignore_until = time.monotonic() + 0.5

        device = self.get_default_input_device()

        with sd.InputStream(
            device=device,
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="float32",
            blocksize=self.CHUNK_SIZE
        ) as stream:

            while True:

                chunk, overflowed = stream.read(self.CHUNK_SIZE)
                chunk = chunk.flatten()

                now = time.monotonic()

                # Discard everything while Lumina is speaking.
                if TTS_PLAYING.is_set():

                    recording.clear()
                    self.pre_buffer.clear()

                    recording_started = False
                    silence_start = None

                    ignore_until = now + 0.5

                    continue

                # Allow microphone and audio output to settle.
                if now < ignore_until:

                    self.pre_buffer.clear()
                    continue

                self.pre_buffer.extend(chunk)

                speaking = self.vad.is_speech(chunk)

                if not recording_started:

                    if speaking:

                        print("Speech detected.")

                        recording_started = True

                        recording.append(
                            np.array(self.pre_buffer)
                        )

                    continue

                recording.append(chunk)

                if speaking:

                    silence_start = None

                else:

                    if silence_start is None:
                        silence_start = now

                    elif now - silence_start >= self.SILENCE_SECONDS:

                        print("Speech finished.")
                        break

        if not recording:
            return None

        audio = np.concatenate(recording)

        if len(audio) < self.SAMPLE_RATE * 0.3:
            print("Recording too short.")
            return None

        print("Transcribing...")

        text = self.whisper.transcribe(audio)

        if not text or not text.strip():
            print("No speech recognized.")
            return None

        print(f"Recognized: {text}")

        return text
