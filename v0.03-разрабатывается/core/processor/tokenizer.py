# core/processor/tokenizer.py — Токенизация текста v0.0.3
import re
from typing import List
from core.common.utils import clean_text
from core.common.log import get_logger
from config import LOGGING, PROCESSOR

logger = get_logger(__name__)

class Tokenizer:
    def __init__(self):
        self.delimiters = r"[ \t\n\r\f\v.,!?;:\"()\-—]+"
        logger.debug(f"{LOGGING['prefix_system']} Токенизатор инициализирован.")

    def tokenize(self, text: str) -> List[str]:
        """Разбивает строку на токены."""
        cleaned = clean_text(text)
        tokens = re.split(self.delimiters, cleaned)
        tokens = [t for t in tokens if t]

        # Ограничение по количеству токенов
        max_tokens = PROCESSOR.get("max_tokens_per_input", 200)
        if len(tokens) > max_tokens:
            logger.warning(f"{LOGGING['prefix_system']} Превышен лимит токенов ({len(tokens)} > {max_tokens}), обрезаем.")
            tokens = tokens[:max_tokens]

        logger.debug(f"{LOGGING['prefix_system']} Токенизация завершена: {tokens}")
        return tokens

    def count_tokens(self, text: str) -> int:
        return len(self.tokenize(text))

    def preview_tokens(self, text: str) -> None:
        tokens = self.tokenize(text)
        logger.info(f"{LOGGING['prefix_system']} Предпросмотр токенов: {tokens}")
