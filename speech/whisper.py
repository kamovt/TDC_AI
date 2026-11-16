from faster_whisper import WhisperModel


class Whisper:

    def __init__(self):

        print("Loading Whisper...")

        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        print("Whisper ready.")

    def transcribe(self, audio):

        segments, _ = self.model.transcribe(
            audio,
            language="pt",
            beam_size=5
        )

        text = " ".join(
            segment.text
            for segment in segments
        ).strip()

        return text