from abc import ABC, abstractmethod

class AudioInput(ABC):
    @abstractmethod
    def list_devices(self):
        """Вернуть список аудиоустройств"""

    @abstractmethod
    def record(self, duration: float, device=None):
        """Записать аудио определённой длительности"""
