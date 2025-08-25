# core/processor/parser.py
# core/processor/parser.py — Парсер текста v0.0.3
from core.common.types import Phrase, PhraseType
from core.processor.tokenizer import Tokenizer
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer()
        logger.debug(f"{LOGGING['prefix_system']} Парсер инициализирован.")

    def parse(self, text: str) -> Phrase:
        tokens = self.tokenizer.tokenize(text)
        phrase_type = PhraseType.STATEMENT  # TODO: интеграция с Classifier
        logger.debug(f"{LOGGING['prefix_system']} Парсер: текст='{text}', токенов={len(tokens)}")
        return Phrase(text=text, tokens=tokens, phrase_type=phrase_type)
