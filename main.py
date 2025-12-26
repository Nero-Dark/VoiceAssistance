"""
Голосовой ассистент с поддержкой Wake Word и циклом диалога
Использует Vosk для STT и pyttsx3 для TTS
"""
import os
import sys
import queue
import json
import time
from pathlib import Path

import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

from commands import CommandHandler

class VoiceAssistant:
    def __init__(self, 
                 model_path: str = "models/vosk-model-small-ru-0.22",
                 wake_word: str = "ассистент",
                 sample_rate: int = 16000):
        """
        Инициализация голосового ассистента
        
        Args:
            model_path: Путь к модели Vosk
            wake_word: Ключевое слово для активации
            sample_rate: Частота дискретизации аудио
        """
        self.sample_rate = sample_rate
        self.wake_word = wake_word.lower()
        self.is_active = False  # Активен ли диалоговый режим
        self.audio_queue = queue.Queue()
        
        # Проверка модели
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Модель не найдена: {model_path}\n"
                f"Скачайте модель с https://alphacephei.com/vosk/models"
            )
        
        print(f"[Загрузка] Модель Vosk из {model_path}...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        print("[OK] Модель загружена")
        
        # Обработчик команд
        self.command_handler = CommandHandler()
        
        # Время последней активности
        self.last_activity_time = time.time()
        self.dialogue_timeout = 15  # Таймаут неактивности в диалоге (секунды)
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback для обработки входящего аудио"""
        if status:
            print(f"[Аудио] Статус: {status}")
        self.audio_queue.put(bytes(indata))
    
    def process_audio(self, audio_data):
        """Обработка аудио данных"""
        if self.recognizer.AcceptWaveform(audio_data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            
            if text:
                return text
        
        return None
    
    def check_wake_word(self, text: str) -> bool:
        """Проверка наличия ключевого слова"""
        text_lower = text.lower().strip()
        
        # Варианты распознавания wake word
        wake_word_variants = [
            self.wake_word,
            self.wake_word.replace('е', 'и'),  # ассистент -> ассистинт
            self.wake_word.replace('и', 'е'),
            'асистент',
            'ассистент',
            'ассистенты',
            'асистенты',
        ]
        
        # Проверяем точное совпадение и вхождение
        for variant in wake_word_variants:
            if variant in text_lower or text_lower in variant:
                print(f"[DEBUG] Найдено ключевое слово: '{variant}' в '{text_lower}'")
                return True
        
        return False
    
    def check_goodbye(self, text: str) -> bool:
        """Проверка на слова прощания"""
        text_lower = text.lower()
        
        goodbye_words = [
            'пока',
            'до свидания',
            'досвидания',
            'спасибо пока',
            'всё спасибо',
            'хватит',
            'стоп',
            'закончили',
            'завершить',
            'выход',
            'отмена',
            'всё',
            'достаточно',
        ]
        
        for word in goodbye_words:
            if word in text_lower:
                return True
        
        return False
    
    def listen_for_wake_word(self):
        """Режим ожидания ключевого слова"""
        print(f"\n[Режим ожидания] Скажите '{self.wake_word}' для активации...")
        print(f"[DEBUG] Всё распознанное будет показано для отладки")
        
        while not self.is_active:
            try:
                data = self.audio_queue.get(timeout=1)
                text = self.process_audio(data)
                
                if text:
                    print(f"[Услышано]: '{text}'")
                    
                    if self.check_wake_word(text):
                        print(f"\n{'='*60}")
                        print(f"  ✓ АССИСТЕНТ АКТИВИРОВАН")
                        print(f"{'='*60}")
                        self.command_handler.speak("Да, слушаю вас")
                        self.is_active = True
                        self.last_activity_time = time.time()
                        
                        # Очищаем очередь
                        while not self.audio_queue.empty():
                            self.audio_queue.get()
                        
                        return True
                    
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                return False
        
        return False
    
    def listen_for_command(self, timeout: float = 10.0):
        """
        Режим прослушивания команды с таймаутом
        
        Args:
            timeout: Максимальное время ожидания речи
            
        Returns:
            Распознанный текст или None
        """
        print("\n[Слушаю] Говорите команду...")
        
        start_time = time.time()
        command_parts = []
        silence_start = time.time()
        silence_threshold = 1.5  # Секунд тишины для завершения команды
        
        while time.time() - start_time < timeout:
            try:
                data = self.audio_queue.get(timeout=0.1)
                text = self.process_audio(data)
                
                if text:
                    command_parts.append(text)
                    silence_start = time.time()  # Сбрасываем таймер тишины
                    print(f"[Распознано]: {text}")
                else:
                    # Проверяем тишину
                    if command_parts and (time.time() - silence_start) > silence_threshold:
                        break
                    
            except queue.Empty:
                # Проверяем тишину
                if command_parts and (time.time() - silence_start) > silence_threshold:
                    break
                continue
        
        # Получаем финальный результат
        try:
            final_result = json.loads(self.recognizer.FinalResult())
            final_text = final_result.get("text", "")
            if final_text and final_text not in command_parts:
                command_parts.append(final_text)
        except:
            pass
        
        full_command = " ".join(command_parts).strip()
        
        if full_command:
            print(f"\n[Команда получена]: {full_command}")
            self.last_activity_time = time.time()
            return full_command
        else:
            print("[Таймаут] Команда не распознана")
            return None
    
    def execute_command(self, command: str) -> bool:
        """
        Выполнение команды
        
        Returns:
            True если нужно продолжить диалог, False если нужно завершить
        """
        if not command:
            self.command_handler.speak("Я вас не расслышала. Повторите, пожалуйста")
            return True
        
        # Проверка на прощание
        if self.check_goodbye(command):
            print(f"\n{'='*60}")
            print(f"  ✓ ЗАВЕРШЕНИЕ ДИАЛОГА")
            print(f"{'='*60}\n")
            self.command_handler.speak("До свидания! Обращайтесь ещё")
            return False
        
        # Выполнение команды
        success = self.command_handler.execute(command)
        
        if not success:
            self.command_handler.speak("Извините, я не поняла команду. Попробуйте ещё раз или скажите 'помощь'")
        
        # Продолжаем диалог в любом случае
        return True
    
    def dialogue_mode(self):
        """Режим диалога - цикл команд"""
        print("\n[Режим диалога] Можете задавать команды")
        print("Для выхода скажите: 'пока', 'до свидания', 'хватит' или 'стоп'\n")
        
        while self.is_active:
            # Проверка таймаута неактивности
            if time.time() - self.last_activity_time > self.dialogue_timeout:
                print(f"\n[Таймаут] {self.dialogue_timeout} секунд без активности")
                self.command_handler.speak("Вы ещё здесь? Если нужна помощь - я слушаю")
                self.last_activity_time = time.time()
                
                # Ждём ещё немного
                waited = 0
                while waited < 5:
                    if not self.audio_queue.empty():
                        break
                    time.sleep(0.5)
                    waited += 0.5
                else:
                    # Совсем нет активности - выходим
                    print("\n[Автовыход] Завершаю диалог из-за длительной неактивности")
                    self.command_handler.speak("До свидания!")
                    self.is_active = False
                    break
            
            # Слушаем команду
            command = self.listen_for_command()
            
            # Выполняем команду
            should_continue = self.execute_command(command)
            
            if not should_continue:
                self.is_active = False
                break
            
            # Небольшая пауза перед следующей командой
            print("\n" + "-"*60)
            print("[Готов] Слушаю следующую команду...")
            print("       (Или скажите 'пока' для выхода)")
            print("-"*60)
    
    def run(self):
        """Основной цикл работы ассистента"""
        print("\n" + "="*60)
        print("  ГОЛОСОВОЙ АССИСТЕНТ")
        print("="*60)
        print(f"Ключевое слово для активации: '{self.wake_word}'")
        print(f"Таймаут диалога: {self.dialogue_timeout} секунд")
        print("Для выхода из программы: Ctrl+C")
        print("="*60 + "\n")
        
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            ):
                while True:
                    # Режим ожидания wake word
                    if not self.is_active:
                        if not self.listen_for_wake_word():
                            break
                    
                    # Режим диалога (цикл команд)
                    if self.is_active:
                        self.dialogue_mode()
                        
                        # После выхода из диалога
                        print("\n[Возврат] Возвращаюсь в режим ожидания...\n")
                        time.sleep(1)
                        
        except KeyboardInterrupt:
            print("\n\n[Завершение работы]")
            self.command_handler.speak("До свидания!")
        except Exception as e:
            print(f"\n[ОШИБКА]: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nАссистент остановлен.")


def main():
    """Точка входа"""
    # Настройка путей
    MODEL_PATH = "models/stt/vosk-model-small-ru-0.22"
    WAKE_WORD = "ассистент"
    DIALOGUE_TIMEOUT = 15  # секунд
    
    # Проверка наличия модели
    if not os.path.exists(MODEL_PATH):
        print(f"\n[ОШИБКА] Модель не найдена: {MODEL_PATH}")
        print("\nСкачайте русскую модель Vosk:")
        print("1. Перейдите на https://alphacephei.com/vosk/models")
        print("2. Скачайте 'vosk-model-small-ru-0.22'")
        print(f"3. Распакуйте в папку: {MODEL_PATH}")
        print()
        return 1
    
    try:
        assistant = VoiceAssistant(
            model_path=MODEL_PATH,
            wake_word=WAKE_WORD
        )
        assistant.dialogue_timeout = DIALOGUE_TIMEOUT
        assistant.run()
        return 0
        
    except Exception as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА]: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())