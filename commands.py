import re
import json
import pyttsx3
from typing import Callable, Dict

class CommandHandler:
    def __init__(self, config_path: str = "commands.json"):
        self.engine = pyttsx3.init()
        self.commands: Dict = {}
        # Маппинг ключей из JSON к методам класса
        self.action_map: Dict[str, Callable] = {
            "greeting": lambda text: self.speak("Привет! Чем могу помочь?"),
            "farewell": lambda text: (self.speak("До свидания!"), exit()),
            "get_time": self._get_time,
            "get_date": self._get_date,
            "music_play": lambda text: self.speak("Включаю музыку"),
            "music_pause": lambda text: self.speak("Музыка на паузе"),
            "music_next": lambda text: self.speak("Переключаю вперед"),
            "music_prev": lambda text: self.speak("Возвращаю назад"),
            "music_volume": self._control_volume,
            "help": self._show_help
        }
        self._load_commands(config_path)

    def _load_commands(self, path: str):
        """Загрузка фраз из JSON и компиляция в регулярные выражения"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for action_key, info in data.items():
                    if action_key in self.action_map:
                        # Объединяем синонимы через ИЛИ
                        pattern = "|".join(info['patterns'])
                        self.commands[pattern] = {
                            'handler': self.action_map[action_key],
                            'description': info.get('description', '')
                        }
        except Exception as e:
            print(f"[Ошибка загрузки JSON]: {e}")

    def speak(self, text: str):
        print(f"[Ассистент]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def _music_play(self, text: str):
        self.speak("Запускаю")
        os.system("playerctl play") # Или ваша команда, например: mocp -p

    def _music_pause(self, text: str):
        self.speak("Ставлю на паузу")
        os.system("playerctl pause") # Или ваша command, например: mocp -s

    def _music_next(self, text: str):
        self.speak("Следующий трек")
        os.system("playerctl next") # Или: mocp -f

    def _music_prev(self, text: str):
        self.speak("Предыдущий трек")
        os.system("playerctl previous") # Или: mocp -r

    def _get_time(self, text: str):
        from datetime import datetime
        self.speak(f"Сейчас {datetime.now().strftime('%H:%M')}")

    def _get_date(self, text: str):
        from datetime import datetime
        now = datetime.now()
        self.speak(f"Сегодня {now.day}.{now.month}.{now.year}")

    def _control_light(self, text: str):
        if "включи" in text.lower() or "зажги" in text.lower():
            self.speak("Включаю свет")
        else:
            self.speak("Выключаю свет")
            
    def _control_volume(self, text: str):
        """Управление громкостью через amixer (Unix)"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            level = int(numbers[0])
            if 0 <= level <= 100:
                os.system(f"amixer set Master {level}%")
                self.speak(f"Громкость {level} процентов")
                return

        if "громче" in text or "больше" in text:
            os.system("amixer set Master 10%+")
            self.speak("Прибавила громкость")
        elif "тише" in text or "меньше" in text:
            os.system("amixer set Master 10%-")
            self.speak("Убавила громкость")
        else:
            self.speak("Не поняла уровень громкости")

    def _show_help(self, text: str):
        descriptions = [cmd['description'] for cmd in self.commands.values() if cmd['description']]
        self.speak("Я умею: " + ", ".join(descriptions))

    def execute(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern, cmd_info in self.commands.items():
            if re.search(pattern, text_lower):
                try:
                    cmd_info['handler'](text)
                    return True
                except Exception as e:
                    print(f"[Ошибка]: {e}")
                    return False
        return False

# Инициализация
_handler = CommandHandler()

def execute_command(text: str) -> bool:
    return _handler.execute(text)

def speak(text: str):
    _handler.speak(text)