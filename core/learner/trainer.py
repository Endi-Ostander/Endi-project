# core/learner/trainer.py — Тренер ИИ v0.0.3
from core.processor.tokenizer import Tokenizer
from core.processor.classifier import Classifier
from core.memory.memory import Memory
from core.learner.rules import rules_engine
from core.learner.curiosity import Curiosity
from core.learner.generator import Generator
from core.thinker.planner import Planner
from core.thinker.self_report import SelfReporter
from core.processor.spellchecker import SpellCorrector
from core.common.log import get_logger
from core.common.utils import clean_text, is_ignorable, is_valid_statement
from core.thinker.meta_journal import MetaJournal
from config import MEMORY, LOGGING, CURIOSITY_PATH, KNOWLEDGE_PATH


logger = get_logger(__name__)

class Trainer:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.classifier = Classifier()
        self.memory = Memory(
            memory_path=MEMORY.get("memory_file"),
            knowledge_path=KNOWLEDGE_PATH
        )
        self.curiosity = Curiosity()
        self.curiosity_path = CURIOSITY_PATH
        self.curiosity.load(self.curiosity_path)
        self.curiosity.save(self.curiosity_path)
        self.generator = Generator(memory=self.memory)
        self.planner = Planner(curiosity=self.curiosity)
        self.spellchecker = SpellCorrector()
        self.reporter = SelfReporter()
        self.journal = MetaJournal()
        self.awaiting_clarification = False
        self.last_question = None
        self.last_input = None
        self.last_response = None
        logger.debug(f"{LOGGING['prefix_system']} Trainer инициализирован.")

    def process_text(self, text: str):
        if self.awaiting_clarification:
            logger.info(f"{LOGGING['prefix_system']} Уточнение к вопросу: {self.last_question}")
            self.memory.add_fact_from_text(text)
            self.journal.record_clarification_response(text, question=self.last_question)
            self.reporter.log_action(f"Получено уточнение: {text}")
            self.awaiting_clarification = False
            self.last_question = None
            return

        if is_ignorable(text):
            logger.debug(f"{LOGGING['prefix_system']} Игнор: '{text}'")
            return

        text = clean_text(text)
        phrase_type = self.classifier.classify(text)
        tokens = self.tokenizer.tokenize(text)

        if phrase_type.name == "STATEMENT" and not is_valid_statement(tokens):
            logger.warning(f"{LOGGING['prefix_system']} Утверждение отвергнуто: {text}")
            self.reporter.log_action("Фраза отвергнута: недостаточно структуры.")
            return

        corrected = self.spellchecker.correct_tokens(tokens)
        if corrected != tokens:
            logger.info(f"{LOGGING['prefix_system']} Исправлено: {tokens} → {corrected}")
            tokens = corrected

        result = rules_engine.apply_rules(phrase_type, tokens, text)
        if result:
            self._handle_result(result)
        else:
            self._handle_unknown(text)

        response = self.generator.generate_response(phrase_type, tokens)
        logger.info(f"{LOGGING['prefix_system']} Ответ: {response}")
        self.reporter.log_action(f"Ответ: {response}", source="Generator")
        self.journal.record_response(response)
        self.curiosity.save(self.curiosity_path)
        self.last_input = text
        self.last_response = response
        return response

    def _handle_result(self, result: dict):
        if result.get("type") == "fact":
            added = self.memory.add_fact(result["subject"], result["predicate"], result["object"], source=result.get("source"))
            if added:
                msg = f"{result['subject']} — {result['predicate']} — {result['object']}"
                logger.info(f"{LOGGING['prefix_system']} Факт добавлен: {msg}")
                self.reporter.log_action(f"Запомнил факт: {msg}")
                self.journal.record_fact_added(result['subject'], result['predicate'], result['object'])

        elif result.get("type") == "question":
            self.awaiting_clarification = True
            self.last_question = result["text"]
            self.curiosity.add_unknown(result["text"])
            logger.info(f"{LOGGING['prefix_system']} Обнаружен вопрос: {result['text']}")
            self.journal.record_entry(f"Обнаружен вопрос: {result['text']}", tag="question")
            self.journal.record_goal(f"Что значит: '{result['text']}'")

        elif result.get("type") == "concept":
            self.memory.add_knowledge(result["title"], result["content"], result["k_type"], tags=result.get("tags", []))
            logger.info(f"{LOGGING['prefix_system']} Новое знание: {result['title']}")
            self.journal.record_entry(f"Новое знание: {result['title']}", tag="knowledge")

    def _handle_unknown(self, text: str):
        self.curiosity.add_unknown(text)
        logger.warning(f"{LOGGING['prefix_system']} Непонятная фраза: {text}")
        self.reporter.log_action("Неопознанная фраза добавлена в любознательность")
        self.journal.record_unknown_phrase(text)
        question = self.generator.ask_clarification(text)
        self.journal.record_entry(question, tag="clarification")
        self.journal.record_goal(question)
