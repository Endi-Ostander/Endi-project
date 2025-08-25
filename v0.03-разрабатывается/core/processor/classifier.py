# core/processor/classifier.py — Классификатор фраз v0.0.3
from core.common.types import PhraseType
from core.common.log import get_logger
from config import QUESTION_STARTERS, COMMAND_VERBS, LOGGING

logger = get_logger(__name__)

class Classifier:
    def __init__(self):
        self.question_starters = QUESTION_STARTERS
        self.command_verbs = COMMAND_VERBS
        logger.debug(f"{LOGGING['prefix_system']} Классификатор инициализирован.")

    def classify(self, text: str) -> PhraseType:
        lowered = text.strip().lower()
        if not text:
            logger.warning(f"{LOGGING['prefix_system']} Пустая строка для классификации.")
            return PhraseType.UNKNOWN
        if text.startswith("/"):
            return PhraseType.COMMAND
        if all(c == '?' for c in lowered):
            return PhraseType.UNKNOWN
        if lowered.endswith("?"):
            return PhraseType.QUESTION
        if any(lowered.startswith(q) for q in self.question_starters):
            return PhraseType.QUESTION
        if any(lowered.startswith(cmd) for cmd in self.command_verbs):
            return PhraseType.COMMAND
        if lowered.endswith(".") or " " in lowered:
            return PhraseType.STATEMENT
        return PhraseType.UNKNOWN
