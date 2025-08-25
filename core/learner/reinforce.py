# core/learner/reinforce.py — Подкрепление знаний v0.0.3
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Reinforce:
    """
    Модуль подкрепления обучения ИИ.
    Можно развить: усиление весов знаний или правил по частоте использования.
    """
    def __init__(self):
        self.rewards = {}
        logger.debug(f"{LOGGING['prefix_system']} Reinforce инициализирован.")

    def reinforce_fact(self, fact_id: str):
        self.rewards[fact_id] = self.rewards.get(fact_id, 0) + 1
        logger.info(f"{LOGGING['prefix_system']} Усиление факта {fact_id}: {self.rewards[fact_id]}")

    def get_reward(self, fact_id: str) -> int:
        return self.rewards.get(fact_id, 0)
