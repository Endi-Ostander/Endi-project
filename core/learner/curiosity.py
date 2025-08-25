# core/learner/curiosity.py — Любознательность v0.0.3
import json
import os
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Curiosity:
    def __init__(self):
        self.unknown_phrases = []
        logger.debug(f"{LOGGING['prefix_system']} Модуль Curiosity инициализирован.")

    def add_unknown(self, phrase: str):
        if phrase not in self.unknown_phrases:
            self.unknown_phrases.append(phrase)
            logger.info(f"{LOGGING['prefix_system']} Добавлена непонятная фраза: '{phrase}'")

    def get_questions(self):
        return [f"Что значит: '{p}'" for p in self.unknown_phrases]

    def get_all(self) -> list[str]:
        return self.unknown_phrases

    def clear(self):
        self.unknown_phrases.clear()
        logger.info(f"{LOGGING['prefix_system']} Список любознательности очищен.")

    def save(self, path: str):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.unknown_phrases, f, ensure_ascii=False, indent=2)
            logger.debug(f"{LOGGING['prefix_system']} Любознательность сохранена в {path}")
        except IOError as e:
            logger.error(f"{LOGGING['prefix_system']} Ошибка сохранения любознательности: {e}")

    def load(self, path: str):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    self.unknown_phrases = json.loads(content) if content else []
                logger.debug(f"{LOGGING['prefix_system']} Загружено фраз: {len(self.unknown_phrases)} из {path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"{LOGGING['prefix_system']} Ошибка загрузки любознательности: {e}")
                self.unknown_phrases = []
