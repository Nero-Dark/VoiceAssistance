import wave
import json
from vosk import Model, KaldiRecognizer

class WakeWord:
    def __init__(self, model_path: str, keyword: str):
        self.model = Model(model_path)
        self.keyword = keyword.lower()

    def check_wakeword(self, filename: str) -> bool:
        wf = wave.open(filename, "rb")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "").lower()
                if self.keyword in text:
                    return True
        # проверяем последний кусок
        res = json.loads(rec.FinalResult())
        text = res.get("text", "").lower()
        return self.keyword in text
