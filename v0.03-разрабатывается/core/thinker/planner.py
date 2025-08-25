# core/thinker/planner.py — Планировщик целей v0.0.3
from core.learner.curiosity import Curiosity
from core.thinker.meta_journal import MetaJournal
from core.common.utils import timestamp
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Planner:
    """
    Планировщик: анализирует список непонятых фраз и формирует цели для изучения.
    """
    def __init__(self, curiosity: Curiosity):
        self.curiosity = curiosity
        self.journal = MetaJournal()
        logger.debug(f"{LOGGING['prefix_system']} Planner инициализирован.")

    def plan(self) -> list[str]:
        questions = self.curiosity.get_questions()
        if not questions:
            logger.info(f"{LOGGING['prefix_system']} Планировщик: открытых вопросов нет.")
            return ["На данный момент у меня нет открытых вопросов."]

        existing_goals = self.journal.get_logged_goals()
        new_goals = [q for q in questions if q not in existing_goals]

        logger.debug(f"{LOGGING['prefix_system']} Новых целей: {len(new_goals)}")
        return new_goals or ["На данный момент у меня нет открытых вопросов."]

    def describe(self) -> str:
        return "Я анализирую неизвестные фразы и планирую, что изучить дальше."

    def debug_info(self) -> str:
        return f"[Planner@{timestamp()}] вопросов в очереди: {len(self.curiosity.get_all())}"
