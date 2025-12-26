"""
Модуль для обработки голосовых команд
"""
import re
from typing import Optional, Callable
import pyttsx3

class CommandHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.commands = {}
        self._register_default_commands()
    
    def speak(self, text: str):
        """Озвучивание текста"""
        print(f"[Ассистент]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def register_command(self, pattern: str, handler: Callable, description: str = ""):
        """Регистрация новой команды"""
        self.commands[pattern] = {
            'handler': handler,
            'description': description
        }
    
    def _register_default_commands(self):
        """Регистрация стандартных команд"""
        
        # Приветствие
        self.register_command(
            r"привет|здравствуй|добрый день|добрый вечер|доброе утро|здорово",
            self._greeting,
            "Приветствие"
        )
        
        # Время
        self.register_command(
            r"сколько времени|который час|время|часы",
            self._get_time,
            "Узнать текущее время"
        )
        
        # Дата
        self.register_command(
            r"какое сегодня число|какая дата|какое число|сегодня|дата",
            self._get_date,
            "Узнать текущую дату"
        )
        
        # День недели
        self.register_command(
            r"какой день недели|какой сегодня день",
            self._get_day_of_week,
            "Узнать день недели"
        )
        
        # Помощь
        self.register_command(
            r"помощь|что ты умеешь|команды|помоги|справка",
            self._show_help,
            "Показать список команд"
        )
        
        # Как дела
        self.register_command(
            r"как дела|как ты|как поживаешь|как настроение",
            lambda text: self.speak("Отлично, спасибо! Готова помочь вам"),
            "Узнать, как дела у ассистента"
        )
        
        # Спасибо
        self.register_command(
            r"спасибо|благодарю|спс",
            lambda text: self.speak("Всегда пожалуйста! Обращайтесь ещё"),
            "Благодарность"
        )
        
        # Повтори
        self.register_command(
            r"повтори|ещё раз|не расслышал",
            lambda text: self.speak("Извините, я не помню предыдущую фразу. Задайте вопрос заново"),
            "Попросить повторить"
        )
        
        # Погода (заглушка)
        self.register_command(
            r"какая погода|погода",
            lambda text: self.speak("К сожалению, функция погоды пока не подключена. Но я могу показать вам время"),
            "Узнать погоду"
        )
        
        # Музыка (заглушка)
        self.register_command(
            r"включи музыку|музыка|поставь музыку",
            lambda text: self.speak("Функция управления музыкой в разработке"),
            "Управление музыкой"
        )
        
        # Умный дом (заглушка)
        self.register_command(
            r"включи свет|выключи свет|свет",
            self._control_light,
            "Управление светом"
        )
        
        # Шутка
        self.register_command(
            r"расскажи шутку|пошути|анекдот",
            self._tell_joke,
            "Рассказать шутку"
        )
        
        # Кто ты
        self.register_command(
            r"кто ты|как тебя зовут|твоё имя",
            lambda text: self.speak("Я голосовой ассистент. Создана помогать вам с разными задачами"),
            "Узнать, кто ты"
        )
    
    def _greeting(self, text: str):
        """Приветствие с учетом времени суток"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 17:
            greeting = "Добрый день"
        elif 17 <= hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"
        
        self.speak(f"{greeting}! Чем могу помочь?")
    
    def _get_time(self, text: str):
        """Получить текущее время"""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime("%H часов %M минут")
        self.speak(f"Сейчас {time_str}")
    
    def _get_date(self, text: str):
        """Получить текущую дату"""
        from datetime import datetime
        now = datetime.now()
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        date_str = f"{now.day} {months[now.month - 1]} {now.year} года"
        self.speak(f"Сегодня {date_str}")
    
    def _get_day_of_week(self, text: str):
        """Получить день недели"""
        from datetime import datetime
        now = datetime.now()
        days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        day = days[now.weekday()]
        self.speak(f"Сегодня {day}")
    
    def _show_help(self, text: str):
        """Показать список доступных команд"""
        help_text = "Вот что я умею: узнать время, дату, день недели. Могу пошутить. Могу рассказать о себе. Для выхода скажите пока или до свидания"
        self.speak(help_text)
    
    def _tell_joke(self, text: str):
        """Рассказать шутку"""
        import random
        jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что 31 октября равно 25 декабря в восьмеричной системе!",
            "Заходит программист в бар. Бармен спрашивает: вам обычное? Программист отвечает: нет, исключение!",
            "Как называется программист после работы? Уставший баг!",
            "Почему компьютер пошёл к врачу? У него был вирус!",
            "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это аппаратная проблема!"
        ]
        joke = random.choice(jokes)
        self.speak(joke)
    
    def _control_light(self, text: str):
        """Управление светом (заглушка для интеграции с Home Assistant)"""
        if "включи" in text.lower():
            self.speak("Включаю свет. Эта функция в разработке, но я уже запомнила команду")
        elif "выключи" in text.lower():
            self.speak("Выключаю свет. Эта функция в разработке, но я уже запомнила команду")
        else:
            self.speak("Скажите включи свет или выключи свет")
    
    def execute(self, text: str) -> bool:
        """
        Выполнить команду на основе распознанного текста
        Возвращает True если команда найдена, False иначе
        """
        text_lower = text.lower()
        
        # Проверяем все зарегистрированные команды
        for pattern, cmd_info in self.commands.items():
            if re.search(pattern, text_lower):
                try:
                    cmd_info['handler'](text)
                    return True
                except Exception as e:
                    print(f"[Ошибка выполнения команды]: {e}")
                    self.speak("Извините, произошла ошибка при выполнении команды")
                    return False
        
        return False


# Для обратной совместимости с main.py
_handler = CommandHandler()

def execute_command(text: str) -> bool:
    """Функция-обертка для старого кода"""
    return _handler.execute(text)


def speak(text: str):
    """Функция-обертка для озвучивания"""
    _handler.speak(text)