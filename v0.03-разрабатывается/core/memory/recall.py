# core/memory/recall.py — Извлечение памяти v0.0.3
from core.memory.memory import Memory
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Recall:
    """
    Модуль для извлечения и поиска информации из памяти.
    Делегирует функции объекту Memory.
    """
    def __init__(self):
        self.memory = Memory()
        logger.debug(f"{LOGGING['prefix_memory']} Модуль Recall инициализирован.")

    def recall_facts(self, subject: str):
        facts = self.memory.find_facts_by_subject(subject)
        logger.info(f"{LOGGING['prefix_memory']} Найдено фактов по '{subject}': {len(facts)}")
        return facts

    def recall_knowledge(self, tag: str):
        knowledge = self.memory.find_knowledge_by_tag(tag)
        logger.info(f"{LOGGING['prefix_memory']} Найдено знаний по тегу '{tag}': {len(knowledge)}")
        return knowledge
