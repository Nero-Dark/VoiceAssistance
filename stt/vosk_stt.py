import wave
import json
from vosk import Model, KaldiRecognizer
from stt.base import STT

class VoskSTT(STT):
    def __init__(self, model_path: str):
        print(f"Loading Vosk model from {model_path}...")
        self.model = Model(model_path)
        print("Model loaded.")

    def transcribe(self, filename: str) -> str:
        wf = wave.open(filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100, 48000]:
            raise ValueError("Vosk требует WAV PCM16 mono с частотой 8/16/32/44/48kHz")

        rec = KaldiRecognizer(self.model, wf.getframerate())
        result_text = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += res.get("text", "") + " "

        # Последние результаты
        res = json.loads(rec.FinalResult())
        result_text += res.get("text", "")
        return result_text.strip()
