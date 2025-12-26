"""
TTS реализация на базе pyttsx3
"""
import pyttsx3
from typing import Optional, Dict, Any
from tts.base import TTS


class Pyttsx3TTS(TTS):
    """
    Text-to-Speech система на базе pyttsx3
    Использует системные голоса (SAPI5 на Windows, NSSpeechSynthesizer на Mac)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация pyttsx3 TTS
        
        Args:
            config: Конфигурация:
                - voice: ID голоса
                - rate: Скорость речи (слова в минуту, по умолчанию 150)
                - volume: Громкость (0.0-1.0, по умолчанию 0.9)
                - language: Язык ('ru', 'en')
        """
        super().__init__(config)
        
        # Инициализация движка
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            raise RuntimeError(f"Не удалось инициализировать pyttsx3: {e}")
        
        # Настройка параметров
        self._setup_engine()
        
        self.is_initialized = True
    
    def _setup_engine(self):
        """Настройка параметров движка"""
        # Скорость речи
        rate = self.config.get('rate', 150)
        self.engine.setProperty('rate', rate)
        
        # Громкость
        volume = self.config.get('volume', 0.9)
        self.engine.setProperty('volume', volume)
        
        # Голос
        voice_id = self.config.get('voice')
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # Пытаемся найти русский голос
            self._set_russian_voice()
    
    def _set_russian_voice(self):
        """Установить русский голос, если доступен"""
        voices = self.engine.getProperty('voices')
        
        # Поиск русского голоса
        for voice in voices:
            # Проверяем наличие русского языка в ID или имени
            if 'ru' in voice.id.lower() or 'russian' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                print(f"[TTS] Установлен русский голос: {voice.name}")
                return
        
        # Если не нашли, используем первый доступный
        if voices:
            self.engine.setProperty('voice', voices[0].id)
            print(f"[TTS] Русский голос не найден, используется: {voices[0].name}")
    
    def synthesize(self, text: str, output_path: str):
        """
        Синтезировать речь и сохранить в файл
        
        Args:
            text: Текст для озвучивания
            output_path: Путь для сохранения
        """
        self.validate_output_path(output_path)
        
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            print(f"[TTS] Аудио сохранено: {output_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка синтеза: {e}")
    
    def speak(self, text: str):
        """
        Озвучить текст напрямую
        
        Args:
            text: Текст для озвучивания
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Ошибка озвучивания: {e}")
    
    def get_available_voices(self) -> list:
        """
        Получить список доступных голосов
        
        Returns:
            Список словарей с информацией о голосах
        """
        voices = self.engine.getProperty('voices')
        
        result = []
        for voice in voices:
            result.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': getattr(voice, 'gender', 'unknown'),
                'age': getattr(voice, 'age', 'unknown')
            })
        
        return result
    
    def print_available_voices(self):
        """Вывести информацию о доступных голосах"""
        voices = self.get_available_voices()
        
        print("\n" + "="*60)
        print("  ДОСТУПНЫЕ ГОЛОСА")
        print("="*60)
        
        for i, voice in enumerate(voices, 1):
            print(f"\n[{i}] {voice['name']}")
            print(f"    ID: {voice['id']}")
            print(f"    Языки: {voice['languages']}")
            print(f"    Пол: {voice['gender']}")
        
        print("\n" + "="*60 + "\n")
    
    def set_voice_by_name(self, name: str):
        """
        Установить голос по имени
        
        Args:
            name: Часть имени голоса для поиска
        """
        voices = self.engine.getProperty('voices')
        
        for voice in voices:
            if name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                print(f"[TTS] Установлен голос: {voice.name}")
                return True
        
        print(f"[TTS] Голос с именем '{name}' не найден")
        return False
    
    def set_speed(self, speed: float):
        """
        Установить скорость речи
        
        Args:
            speed: Множитель скорости (0.5 - 2.0)
        """
        super().set_speed(speed)
        
        # Базовая скорость 150 слов/мин
        base_rate = 150
        new_rate = int(base_rate * speed)
        
        self.engine.setProperty('rate', new_rate)
        print(f"[TTS] Скорость: {new_rate} слов/мин")
    
    def set_volume(self, volume: float):
        """
        Установить громкость
        
        Args:
            volume: Громкость (0.0 - 1.0)
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Громкость должна быть в диапазоне 0.0-1.0")
        
        self.engine.setProperty('volume', volume)
        self.config['volume'] = volume
        print(f"[TTS] Громкость: {volume}")
    
    def get_current_settings(self) -> dict:
        """
        Получить текущие настройки
        
        Returns:
            Словарь с настройками
        """
        return {
            'rate': self.engine.getProperty('rate'),
            'volume': self.engine.getProperty('volume'),
            'voice': self.engine.getProperty('voice'),
        }
    
    def __del__(self):
        """Очистка ресурсов"""
        try:
            if hasattr(self, 'engine'):
                self.engine.stop()
        except:
            pass


# Пример использования
if __name__ == "__main__":
    # Создание TTS
    tts = Pyttsx3TTS()
    
    # Вывод доступных голосов
    tts.print_available_voices()
    
    # Тест синтеза
    print("\n[Тест] Озвучивание...")
    tts.speak("Привет! Это тест голосового синтеза.")
    
    # Тест с изменением параметров
    print("\n[Тест] Быстрая речь...")
    tts.set_speed(1.5)
    tts.speak("А это быстрая речь")
    
    print("\n[Тест] Медленная речь...")
    tts.set_speed(0.7)
    tts.speak("А это медленная речь")
    
    print("\n[Тест] Сохранение в файл...")
    tts.synthesize("Это сохраненное аудио", "test_output.wav")
    
    print("\n[OK] Все тесты завершены")