import os
import subprocess
from pathlib import Path
from piper.download_voices import download_voice

class PiperTTS:
    def __init__(self, voice="ru_RU-ruslan-medium"):
        self.base_dir = Path("models/tts")
        self.model_dir = self.base_dir / voice
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.voice = voice

        # Проверяем, есть ли уже файлы модели
        model_files = list(self.model_dir.glob("*.onnx"))
        if not model_files:
            print(f"[PiperTTS] Модель {voice} не найдена. Скачиваем...")
            download_voice(voice, download_dir=self.model_dir)
            print(f"[PiperTTS] Модель {voice} скачана в {self.model_dir}")

        # Проверяем, что теперь файлы есть
        model_files = list(self.model_dir.glob("*.onnx"))
        if not model_files:
            raise FileNotFoundError(f"Не найдены файлы модели в {self.model_dir}")
        self.model_path = model_files[0]

        config_files = list(self.model_dir.glob("*.json"))
        self.config_path = config_files[0] if config_files else None

        print(f"[PiperTTS] Модель готова: {self.model_path}, {self.config_path}")

    def synthesize(self, text, output_file):
        """Генерация аудио через CLI"""
        cmd = [
            "python", "-m", "piper",
            "-m", str(self.model_path),
            "--text", text,
            "-f", output_file
        ]
        if self.config_path:
            cmd.extend(["-c", str(self.config_path)])

        print(f"[PiperTTS] Генерируем аудио: {output_file}")
        subprocess.run(cmd, check=True)
        print(f"[PiperTTS] Аудио готово: {output_file}")
