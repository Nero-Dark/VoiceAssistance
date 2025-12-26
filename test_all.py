"""
Скрипт для тестирования микрофона и распознавания речи
"""
import os
import sys
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

def test_audio_devices():
    """Тест 1: Проверка аудио устройств"""
    print("\n" + "="*60)
    print("  ТЕСТ 1: АУДИО УСТРОЙСТВА")
    print("="*60 + "\n")
    
    try:
        devices = sd.query_devices()
        
        print("Доступные устройства:")
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append(f"Вход: {device['max_input_channels']} каналов")
            if device['max_output_channels'] > 0:
                device_type.append(f"Выход: {device['max_output_channels']} каналов")
            
            marker = " [ПО УМОЛЧАНИЮ]" if i == sd.default.device[0] else ""
            print(f"\n[{i}] {device['name']}{marker}")
            print(f"    {', '.join(device_type)}")
            print(f"    Частота: {device['default_samplerate']} Hz")
        
        print(f"\n✓ Устройство ввода по умолчанию: {sd.default.device[0]}")
        print(f"✓ Устройство вывода по умолчанию: {sd.default.device[1]}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_microphone_level():
    """Тест 2: Проверка уровня сигнала с микрофона"""
    print("\n" + "="*60)
    print("  ТЕСТ 2: УРОВЕНЬ СИГНАЛА МИКРОФОНА")
    print("="*60 + "\n")
    
    print("Говорите в микрофон в течение 5 секунд...")
    print("Наблюдайте за уровнем сигнала:\n")
    
    duration = 5  # секунд
    sample_rate = 16000
    
    try:
        def callback(indata, frames, time, status):
            if status:
                print(status)
            
            # Вычисляем уровень сигнала
            volume_norm = abs(indata).mean()
            
            # Визуализация уровня
            bar_length = 50
            filled = int(bar_length * min(volume_norm * 100, 1.0))
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"\r[{bar}] {volume_norm*100:.1f}%", end='', flush=True)
        
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            callback=callback
        ):
            sd.sleep(duration * 1000)
        
        print("\n\n✓ Микрофон работает!")
        print("  Если уровень был низким (< 10%), проверьте:")
        print("  - Настройки громкости микрофона в системе")
        print("  - Правильно ли выбран микрофон")
        print("  - Подключен ли микрофон")
        
        return True
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False


def test_vosk_recognition():
    """Тест 3: Проверка распознавания речи"""
    print("\n" + "="*60)
    print("  ТЕСТ 3: РАСПОЗНАВАНИЕ РЕЧИ (VOSK)")
    print("="*60 + "\n")
    
    model_path = "models/stt/vosk-model-small-ru-0.22"
    
    # Проверка модели
    if not os.path.exists(model_path):
        print(f"✗ Модель не найдена: {model_path}")
        print("\nСкачайте модель:")
        print("  https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
        return False
    
    print(f"✓ Модель найдена: {model_path}")
    print("  Загрузка модели...")
    
    try:
        model = Model(model_path)
        rec = KaldiRecognizer(model, 16000)
        print("✓ Модель загружена")
    except Exception as e:
        print(f"✗ Ошибка загрузки модели: {e}")
        return False
    
    # Тест распознавания
    print("\n" + "-"*60)
    print("ГОВОРИТЕ В МИКРОФОН!")
    print("Тест длится 10 секунд.")
    print("Попробуйте сказать:")
    print("  - 'ассистент'")
    print("  - 'привет'")
    print("  - 'проверка связи'")
    print("-"*60 + "\n")
    
    audio_queue = queue.Queue()
    recognized_texts = []
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue.put(bytes(indata))
    
    try:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=callback
        ):
            import time
            start_time = time.time()
            
            while time.time() - start_time < 10:
                try:
                    data = audio_queue.get(timeout=0.1)
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()
                        
                        if text:
                            print(f"[Распознано]: {text}")
                            recognized_texts.append(text)
                
                except queue.Empty:
                    continue
            
            # Получаем последний результат
            final_result = json.loads(rec.FinalResult())
            final_text = final_result.get("text", "")
            if final_text:
                print(f"[Финальный]: {final_text}")
                recognized_texts.append(final_text)
        
        print("\n" + "-"*60)
        
        if recognized_texts:
            print("✓ УСПЕХ! Распознаны следующие фразы:")
            for text in recognized_texts:
                print(f"  - '{text}'")
            
            # Проверка на wake word
            wake_words = ['ассистент', 'асистент', 'ассистенты']
            found_wake_word = any(
                wake in text.lower() 
                for text in recognized_texts 
                for wake in wake_words
            )
            
            if found_wake_word:
                print("\n✓ Wake word 'ассистент' распознано!")
            else:
                print("\n⚠ Wake word 'ассистент' НЕ распознано")
                print("  Попробуйте:")
                print("  - Говорить громче")
                print("  - Говорить четче")
                print("  - Уменьшить фоновый шум")
            
            return True
        else:
            print("✗ НИЧЕГО НЕ РАСПОЗНАНО")
            print("\nВозможные причины:")
            print("  1. Микрофон не работает")
            print("  2. Уровень сигнала слишком низкий")
            print("  3. Выбран неправильный микрофон")
            print("  4. Проблемы с моделью Vosk")
            print("\nРешения:")
            print("  - Проверьте настройки микрофона в системе")
            print("  - Увеличьте громкость микрофона")
            print("  - Говорите ближе к микрофону")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tts():
    """Тест 4: Проверка синтеза речи"""
    print("\n" + "="*60)
    print("  ТЕСТ 4: СИНТЕЗ РЕЧИ (TTS)")
    print("="*60 + "\n")
    
    try:
        import pyttsx3
        
        print("Инициализация pyttsx3...")
        engine = pyttsx3.init()
        
        print("✓ TTS инициализирован")
        print("\nГолоса:")
        voices = engine.getProperty('voices')
        for i, voice in enumerate(voices[:3]):  # Показываем первые 3
            print(f"  [{i}] {voice.name}")
        
        print("\nВоспроизведение тестовой фразы...")
        engine.say("Привет! Это тест синтеза речи.")
        engine.runAndWait()
        
        print("✓ TTS работает!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("  ДИАГНОСТИКА ГОЛОСОВОГО АССИСТЕНТА")
    print("="*60)
    
    tests = [
        ("Аудио устройства", test_audio_devices),
        ("Уровень микрофона", test_microphone_level),
        ("Распознавание речи", test_vosk_recognition),
        ("Синтез речи", test_tts),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\n[Прервано пользователем]")
            break
        except Exception as e:
            print(f"\n✗ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Итоги
    print("\n" + "="*60)
    print("  ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60 + "\n")
    
    for test_name, result in results.items():
        status = "✓ OK" if result else "✗ FAILED"
        print(f"{status}  {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nВаш голосовой ассистент готов к работе.")
        print("Запустите: python main.py")
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("\nИсправьте проблемы выше перед запуском ассистента.")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nТестирование прервано.")
        sys.exit(0)