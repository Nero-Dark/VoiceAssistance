"""
Базовый класс для систем синтеза речи (TTS)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class TTS(ABC):
    """
    Абстрактный базовый класс для Text-to-Speech систем
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация TTS системы
        
        Args:
            config: Словарь с конфигурацией
        """
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str):
        """
        Синтезировать речь из текста
        
        Args:
            text: Текст для озвучивания
            output_path: Путь для сохранения аудио файла
        """
        pass
    
    def speak(self, text: str):
        """
        Озвучить текст напрямую (без сохранения в файл)
        
        Args:
            text: Текст для озвучивания
        """
        # По умолчанию используем временный файл
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            self.synthesize(text, tmp_path)
            self.play_audio(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def play_audio(self, audio_path: str):
        """
        Воспроизвести аудио файл
        
        Args:
            audio_path: Путь к аудио файлу
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            data, samplerate = sf.read(audio_path)
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print(f"[TTS] Ошибка воспроизведения: {e}")
            # Попытка использовать альтернативный метод
            self._play_audio_fallback(audio_path)
    
    def _play_audio_fallback(self, audio_path: str):
        """
        Альтернативный метод воспроизведения
        
        Args:
            audio_path: Путь к аудио файлу
        """
        import os
        import platform
        
        system = platform.system()
        
        try:
            if system == 'Windows':
                os.system(f'start {audio_path}')
            elif system == 'Darwin':  # macOS
                os.system(f'afplay {audio_path}')
            elif system == 'Linux':
                os.system(f'aplay {audio_path}')
            else:
                print(f"[TTS] Автовоспроизведение не поддерживается на {system}")
        except Exception as e:
            print(f"[TTS] Ошибка воспроизведения (fallback): {e}")
    
    def get_supported_languages(self) -> list:
        """
        Получить список поддерживаемых языков
        
        Returns:
            Список кодов языков
        """
        return ['ru']  # По умолчанию только русский
    
    def set_language(self, language: str):
        """
        Установить язык синтеза
        
        Args:
            language: Код языка (например, 'ru', 'en')
        """
        if language not in self.get_supported_languages():
            raise ValueError(f"Язык {language} не поддерживается")
        
        self.config['language'] = language
    
    def set_voice(self, voice: str):
        """
        Установить голос для синтеза
        
        Args:
            voice: Название голоса
        """
        self.config['voice'] = voice
    
    def set_speed(self, speed: float):
        """
        Установить скорость речи
        
        Args:
            speed: Скорость (0.5 - 2.0, где 1.0 - нормальная)
        """
        if not 0.5 <= speed <= 2.0:
            raise ValueError("Скорость должна быть в диапазоне 0.5-2.0")
        
        self.config['speed'] = speed
    
    def set_pitch(self, pitch: float):
        """
        Установить тон голоса
        
        Args:
            pitch: Тон (0.5 - 2.0, где 1.0 - нормальный)
        """
        if not 0.5 <= pitch <= 2.0:
            raise ValueError("Тон должен быть в диапазоне 0.5-2.0")
        
        self.config['pitch'] = pitch
    
    def validate_output_path(self, output_path: str) -> bool:
        """
        Проверить корректность пути для сохранения
        
        Args:
            output_path: Путь для сохранения
            
        Returns:
            True если путь корректный
        """
        path = Path(output_path)
        
        # Проверка расширения
        valid_extensions = {'.wav', '.mp3', '.ogg'}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Неподдерживаемый формат: {path.suffix}")
        
        # Проверка возможности записи в директорию
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def __repr__(self):
        return f"{self.__class__.__name__}(config={self.config})"