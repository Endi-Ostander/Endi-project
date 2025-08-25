# core/memory/update.py — Обновление памяти v0.0.3
from core.memory.memory import Memory
from core.common.types import Fact
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class UpdateMemory:
    """
    Модуль обновления существующих фактов в памяти.
    Простая замена факта по ID.
    """
    def __init__(self):
        self.memory = Memory()
        logger.debug(f"{LOGGING['prefix_memory']} Модуль UpdateMemory инициализирован.")

    def update_fact(self, fact_id: str, new_subject: str, new_predicate: str, new_obj: str):
        updated = False
        for i, fact in enumerate(self.memory.facts):
            if fact.id == fact_id:
                self.memory.facts[i] = Fact(fact_id, new_subject, new_predicate, new_obj, fact.source, fact.timestamp)
                updated = True
                break
        if updated:
            self.memory._save_facts()
            logger.info(f"{LOGGING['prefix_memory']} Факт {fact_id} обновлён.")
        else:
            logger.warning(f"{LOGGING['prefix_memory']} Факт {fact_id} не найден.")
