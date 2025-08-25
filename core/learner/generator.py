# core/learner/generator.py — Генератор ответов v0.0.3
from core.processor.classifier import PhraseType
from core.memory.memory import Memory
from core.common.utils import timestamp
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Generator:
    """
    Отвечает за формирование базовых реакций ИИ на входящие фразы.
    Учитывает тип фразы и доступный контекст памяти.
    """
    def __init__(self, memory: Memory = None):
        self.memory = memory
        logger.debug(f"{LOGGING['prefix_system']} Генератор инициализирован. Память: {'есть' if memory else 'нет'}")

    def generate_response(self, phrase_type: PhraseType, tokens: list[str], context: dict = None) -> str:
        if phrase_type.name == "QUESTION":
            return self._respond_to_question(tokens)
        if phrase_type.name == "STATEMENT":
            return self._respond_to_statement(tokens)
        if phrase_type.name == "COMMAND":
            return "Понял команду, но пока не умею её выполнять."
        return "Я пока не знаю, как на это ответить."

    def _respond_to_question(self, tokens: list[str]) -> str:
        if self.memory and tokens:
            keyword = tokens[-1]
            found = self.memory.search_fact_by_token(keyword)
            if found:
                logger.info(f"{LOGGING['prefix_system']} Ответ найден в памяти по ключевому слову '{keyword}'.")
                return f"Вот что я нашёл в своей памяти: {found[0]}"
        return "Пока не знаю ответа, но запомню этот вопрос."

    def _respond_to_statement(self, tokens: list[str]) -> str:
        if self.memory and tokens:
            self.memory.add_fact(tokens[0], "is", " ".join(tokens[1:]))
        return "Хорошо, я запомнил это как утверждение."

    def ask_clarification(self, phrase: str) -> str:
        return f"Ты можешь объяснить, что значит: '{phrase}'?"

    def generate_acknowledgement(self) -> str:
        return "Принято. Записал."

    def generate_error(self, info: str = "") -> str:
        return f"Возникла ошибка. {info}"

    def describe(self) -> str:
        return "Я — генератор ответов. Формирую базовые реакции на вопросы, утверждения и команды."

    def debug_info(self) -> str:
        return f"[Generator@{timestamp()}] memory: {'on' if self.memory else 'off'}"
