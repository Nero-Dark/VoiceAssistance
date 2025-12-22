from abc import ABC, abstractmethod

class STT(ABC):
    @abstractmethod
    def transcribe(self, filename: str) -> str:
        """Возвращает текст из аудио файла"""
