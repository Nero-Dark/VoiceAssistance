import sounddevice as sd
import numpy as np
import wave
from audio.base import AudioInput
import queue

class WindowsAudioInput(AudioInput):
    def list_devices(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            print(f"{i}: {dev['name']} ({'input' if dev['max_input_channels']>0 else 'output'})")
        return devices

    def record(self, duration: float, device=None, filename="output.wav"):
        fs = 16000
        print(f"Recording {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=device)
        sd.wait()
        print("Recording finished, saving...")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())
        print(f"Saved to {filename}")
        return filename

    def record_async(self, device=None, callback=None):
        """
        Асинхронная запись в поток. 
        callback(data: np.ndarray) вызывается на каждом блоке.
        """
        fs = 16000
        q = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            q.put(indata.copy())
            if callback:
                callback(indata.copy())

        stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16',
                                callback=audio_callback, device=device, blocksize=8000)
        stream.start()
        return stream, q
