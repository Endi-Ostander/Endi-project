# core/processor/extractor.py — Извлечение фактов v0.0.3
from typing import Dict, Any, Optional
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Extractor:
    """
    Извлекает простую структуру факта (subject, predicate, object) из токенов.
    """
    def extract_fact(self, tokens: list, raw_text: str) -> Optional[Dict[str, Any]]:
        if len(tokens) < 3:
            logger.debug(f"{LOGGING['prefix_system']} Недостаточно токенов для извлечения факта: {tokens}")
            return None
        fact = {
            "subject": tokens[0],
            "predicate": tokens[1],
            "object": " ".join(tokens[2:]),
            "source": raw_text
        }
        logger.debug(f"{LOGGING['prefix_system']} Извлечён факт: {fact}")
        return fact
