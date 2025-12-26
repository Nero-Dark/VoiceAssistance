"""
Базовый класс для систем распознавания речи (STT)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class STT(ABC):
    """
    Абстрактный базовый класс для Speech-to-Text систем
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация STT системы
        
        Args:
            config: Словарь с конфигурацией
        """
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Распознать речь из аудио файла
        
        Args:
            audio_path: Путь к аудио файлу
            
        Returns:
            Распознанный текст
        """
        pass
    
    def transcribe_stream(self, audio_stream) -> str:
        """
        Распознать речь из аудио потока (опционально)
        
        Args:
            audio_stream: Поток аудио данных
            
        Returns:
            Распознанный текст
        """
        raise NotImplementedError("Streaming не поддерживается этой STT системой")
    
    def validate_audio_format(self, audio_path: str) -> bool:
        """
        Проверить формат аудио файла
        
        Args:
            audio_path: Путь к аудио файлу
            
        Returns:
            True если формат корректный
        """
        path = Path(audio_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")
        
        # Базовая проверка расширения
        valid_extensions = {'.wav', '.mp3', '.ogg', '.flac'}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Неподдерживаемый формат аудио: {path.suffix}")
        
        return True
    
    def get_supported_languages(self) -> list:
        """
        Получить список поддерживаемых языков
        
        Returns:
            Список кодов языков
        """
        return ['ru']  # По умолчанию только русский
    
    def set_language(self, language: str):
        """
        Установить язык распознавания
        
        Args:
            language: Код языка (например, 'ru', 'en')
        """
        if language not in self.get_supported_languages():
            raise ValueError(f"Язык {language} не поддерживается")
        
        self.config['language'] = language
    
    def __repr__(self):
        return f"{self.__class__.__name__}(config={self.config})"