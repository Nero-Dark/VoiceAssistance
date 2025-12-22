import asyncio
import numpy as np
import wave
from audio.input import WindowsAudioInput
from stt.vosk_stt import VoskSTT
from wakeword.openwakeword import WakeWord
from speaker_id.verifier import SpeakerVerifier
from tts.piper_tts import PiperTTS

async def main():
    audio = WindowsAudioInput()
    stt = VoskSTT(model_path="models/stt/ru")
    wake = WakeWord(model_path="models/stt/ru", keyword="эй колонка")
    verifier = SpeakerVerifier()

    tts = PiperTTS(voice="ru_RU-ruslan-medium")
    tts.synthesize("Привет! Как дела?", "output.wav")

    print("Ассистент готов. Слушаем...")

    command_mode = False
    buffer = []

    def process_block(data):
        nonlocal command_mode, buffer
        buffer.append(data)
        if not command_mode:
            # сохраняем фрагмент во временный WAV для проверки wake word
            temp_file = "temp.wav"
            save_wav(np.concatenate(buffer), temp_file)
            if wake.check_wakeword(temp_file):
                print("Wake word обнаружено!")
                command_mode = True
                buffer.clear()

    stream, q = audio.record_async(callback=process_block)

    while True:
        if command_mode:
            print("Записываем команду 3 секунды...")
            await asyncio.sleep(3)  # запись команды
            temp_file = "command.wav"
            save_wav(np.concatenate(buffer), temp_file)
            text = stt.transcribe(temp_file)
            user = verifier.identify(text)
            print(f"Команда: {text}")
            print(f"Пользователь: {user}")
            buffer.clear()
            command_mode = False
        await asyncio.sleep(0.1)  # предотвращаем блокировку

def save_wav(data: np.ndarray, filename: str):
    import wave
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(data.tobytes())

if __name__ == "__main__":
    asyncio.run(main())
    
