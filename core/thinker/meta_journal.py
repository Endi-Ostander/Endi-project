# core/thinker/meta_journal.py — Мета-журнал ИИ v0.0.3
import os
import ast
from core.common.utils import timestamp
from core.common.log import get_logger
from config import LOGGING, META_JOURNAL

logger = get_logger(__name__)

class MetaJournal:
    """
    Хранит размышления ИИ о себе, целях и прогрессе.
    Используется для внутренней осознанности.
    """
    def __init__(self, path: str = None):
        self.path = path or META_JOURNAL["path"]
        self.limit = META_JOURNAL.get("limit", 500)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        logger.debug(f"{LOGGING['prefix_system']} Мета-журнал инициализирован. Путь: {self.path}")

    def record_entry(self, thought: str, tag: str = "general"):
        entry = {"time": timestamp(), "tag": tag, "thought": thought}
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(str(entry) + "\n")
            logger.debug(f"{LOGGING['prefix_system']} Запись добавлена в мета-журнал: {thought}")
        except IOError as e:
            logger.error(f"{LOGGING['prefix_system']} Ошибка записи в мета-журнал: {e}")

    def record_fact_added(self, subject: str, predicate: str, obj: str):
        self.record_entry(f"Я запомнил факт: {subject} — {predicate} — {obj}.", tag="fact")

    def record_unknown_phrase(self, phrase: str):
        self.record_entry(f"Я не понял фразу: '{phrase}'", tag="curiosity")

    def record_response(self, response: str):
        self.record_entry(f"Я ответил: {response}", tag="response")

    def record_goal(self, description: str):
        self.record_entry(f"Цель: {description}", tag="goal")

    def record_reflection(self, insight: str):
        self.record_entry(f"Размышление: {insight}", tag="reflection")

    def record_clarification_response(self, response: str, question: str = None):
        msg = f"Уточняющий ответ: {response}"
        if question:
            msg += f" на вопрос: {question}"
        self.record_entry(msg, tag="clarification")

    def get_recent_entries(self, limit: int = None) -> list[str]:
        """
        Возвращает последние записи из журнала.
        """
        limit = limit or self.limit
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return f.readlines()[-limit:]

    def get_logged_goals(self) -> list[str]:
        """
        Возвращает список целей из журнала.
        """
        if not os.path.exists(self.path):
            return []
        goals = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = ast.literal_eval(line.strip())
                    if isinstance(entry, dict) and entry.get("tag") == "goal":
                        goals.append(entry["thought"])
                except Exception as e:
                    logger.warning(f"{LOGGING['prefix_system']} Ошибка чтения записи журнала: {e}")
        return goals

    def describe(self) -> str:
        return "Я веду мета-журнал, размышляю о своих действиях и целях."

    def debug_info(self) -> str:
        return f"[MetaJournal@{timestamp()}] журнал: {'Да' if os.path.exists(self.path) else 'Нет'}"
