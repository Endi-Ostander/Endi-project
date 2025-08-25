# core/processor/spellchecker.py — Коррекция орфографии v0.0.3
from spellchecker import SpellChecker
from core.common.log import get_logger
from config import LOGGING, DEFAULT_LANGUAGE
logger = get_logger(__name__)

class SpellCorrector:
    def __init__(self):
        self.spell = SpellChecker(language=DEFAULT_LANGUAGE)
        logger.debug(f"{LOGGING['prefix_system']} Модуль SpellCorrector инициализирован.")

    def correct_tokens(self, tokens: list) -> list:
        corrected = []
        for word in tokens:
            correction = self.spell.correction(word)
            corrected_word = correction if correction else word
            corrected.append(corrected_word)
            if corrected_word != word:
                logger.info(f"{LOGGING['prefix_system']} Исправлено: '{word}' → '{corrected_word}'")
        return corrected
