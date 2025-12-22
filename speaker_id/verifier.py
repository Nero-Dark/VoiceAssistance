class SpeakerVerifier:
    """
    Простая заглушка для теста.
    Привязывает команду к пользователю по ключевому слову.
    """
    def __init__(self):
        # ключевые слова для пользователей
        self.users = {
            "NERO": ["моя команда", "мой комп"],
            "OS": ["комп отца", "его комп"]
        }

    def identify(self, text: str) -> str:
        text = text.lower()
        for user, keywords in self.users.items():
            for kw in keywords:
                if kw in text:
                    return user
        return "unknown"
