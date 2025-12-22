from audio.input import WindowsAudioInput
from stt.vosk_stt import VoskSTT
from wakeword.openwakeword import WakeWord
from speaker_id.verifier import SpeakerVerifier

def main():
    audio = WindowsAudioInput()
    stt = VoskSTT(model_path="models/ru")
    wake = WakeWord(model_path="models/ru", keyword="эй колонка")
    verifier = SpeakerVerifier()

    print("Ассистент готов. Скажите 'Эй, колонка'...")

    while True:
        wav_file = audio.record(1)
        if wake.check_wakeword(wav_file):
            print("Wake word обнаружено!")
            wav_file = audio.record(3)
            text = stt.transcribe(wav_file)
            print("Команда:", text)
            user = verifier.identify(text)
            print("Определённый пользователь:", user)
            # здесь можно подключить HA + WoL
            if user == "sasha":
                print("Включаем твой комп через WoL...")
            elif user == "papa":
                print("Включаем его комп через WoL...")
            else:
                print("Неизвестный пользователь.")

if __name__ == "__main__":
    main()
