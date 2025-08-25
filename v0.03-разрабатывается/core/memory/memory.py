# core/memory/memory.py — Память v0.0.3
import os
from typing import List, Optional
from core.common.utils import load_json, save_json, generate_id, timestamp
from core.common.types import Fact, KnowledgeEntry, KnowledgeType
from core.learner.rules import rules_engine
from core.processor.classifier import Classifier
from core.processor.tokenizer import Tokenizer
from core.common.log import get_logger
from config import MEMORY, LOGGING

logger = get_logger(__name__)

class Memory:
    """
    Класс управления памятью ИИ:
    - Хранит факты и знания
    - Позволяет искать по ключевым словам
    - Добавляет новые факты и знания с проверкой
    """

    def __init__(self, memory_path: Optional[str] = None, knowledge_path: Optional[str] = None):
        # Пути к файлам
        self.memory_path = memory_path or MEMORY.get("memory_file", "data/memory.json")
        self.knowledge_path = knowledge_path or MEMORY.get("knowledge_file", "data/knowledge.json")

        # Параметры
        self.max_facts = MEMORY.get("max_facts", 5000)

        # Модули
        self.classifier = Classifier()
        self.tokenizer = Tokenizer()

        # Загружаем память
        self.facts = self._load_facts()
        self.knowledge = self._load_knowledge()

        logger.info(
            f"{LOGGING['prefix_memory']} Память загружена. "
            f"Фактов: {len(self.facts)}, Знаний: {len(self.knowledge)}"
        )

    # === 📥 Загрузка данных ===
    def _load_facts(self) -> List[Fact]:
        if not os.path.exists(self.memory_path):
            logger.warning(f"{LOGGING['prefix_memory']} Файл памяти не найден: {self.memory_path}")
            return []
        try:
            data = load_json(self.memory_path)
            facts = [Fact(**f) for f in data.get("facts", [])]
            logger.debug(f"{LOGGING['prefix_memory']} Загружено фактов: {len(facts)}")
            return facts
        except Exception as e:
            logger.exception(f"{LOGGING['prefix_memory']} Ошибка загрузки фактов: {e}")
            return []

    def _load_knowledge(self) -> List[KnowledgeEntry]:
        if not os.path.exists(self.knowledge_path):
            logger.warning(f"{LOGGING['prefix_memory']} Файл знаний не найден: {self.knowledge_path}")
            return []
        try:
            data = load_json(self.knowledge_path)
            knowledge = [KnowledgeEntry(**k) for k in data.get("entries", [])]
            logger.debug(f"{LOGGING['prefix_memory']} Загружено знаний: {len(knowledge)}")
            return knowledge
        except Exception as e:
            logger.exception(f"{LOGGING['prefix_memory']} Ошибка загрузки знаний: {e}")
            return []

    # === 💾 Сохранение данных ===
    def _save_facts(self):
        try:
            data = {"facts": [f.__dict__ for f in self.facts]}
            save_json(self.memory_path, data)
            logger.info(f"{LOGGING['prefix_memory']} Сохранено фактов: {len(self.facts)}")
        except Exception as e:
            logger.exception(f"{LOGGING['prefix_memory']} Ошибка сохранения фактов: {e}")

    def _save_knowledge(self):
        try:
            data = {
                "entries": [
                    {
                        **k.__dict__,
                        "type": k.type.value if hasattr(k.type, "value") else k.type
                    }
                    for k in self.knowledge
                ]
            }
            save_json(self.knowledge_path, data)
            logger.info(f"{LOGGING['prefix_memory']} Сохранено знаний: {len(self.knowledge)}")
        except Exception as e:
            logger.exception(f"{LOGGING['prefix_memory']} Ошибка сохранения знаний: {e}")

    # === ➕ Добавление данных ===
    def add_fact(self, subject: str, predicate: str, obj: str, source: Optional[str] = None) -> bool:
        """Добавляет новый факт в память с проверкой на уникальность и лимит"""
        if len(self.facts) >= self.max_facts:
            logger.error(f"{LOGGING['prefix_memory']} Превышен лимит фактов ({self.max_facts}).")
            return False

        # Проверка на дубликат
        for f in self.facts:
            if f.subject == subject and f.predicate == predicate and f.obj == obj:
                logger.warning(f"{LOGGING['prefix_memory']} Факт уже существует: {subject} — {predicate} — {obj}")
                return False

        fact = Fact(
            id=generate_id(),
            subject=subject,
            predicate=predicate,
            obj=obj,
            source=source,
            timestamp=timestamp()
        )
        self.facts.append(fact)
        self._save_facts()
        logger.info(f"{LOGGING['prefix_memory']} Новый факт: {subject} — {predicate} — {obj}")
        return True

    def add_knowledge(self, title: str, content: str, k_type: KnowledgeType, tags: List[str]):
        """Добавляет новый элемент знаний"""
        entry = KnowledgeEntry(
            id=generate_id(),
            title=title,
            content=content,
            type=k_type,
            tags=tags,
            created=timestamp()
        )
        self.knowledge.append(entry)
        self._save_knowledge()
        logger.info(f"{LOGGING['prefix_memory']} Новое знание: {title}")

    # === 🔍 Поиск данных ===
    def search_fact_by_token(self, token: str) -> List[str]:
        token = token.lower().strip()
        return [
            f"{f.subject} — {f.predicate} — {f.obj}"
            for f in self.facts
            if token in f.subject.lower() or token in f.obj.lower()
        ]

    def find_facts_by_subject(self, subject: str) -> List[Fact]:
        return [f for f in self.facts if subject.lower() == f.subject.lower()]

    def find_knowledge_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        return [k for k in self.knowledge if tag in k.tags]

    # === 🧠 Извлечение факта из текста ===
    def add_fact_from_text(self, text: str) -> bool:
        """Пытается извлечь факт из текста и сохранить его"""
        try:
            phrase_type = self.classifier.classify(text)
            tokens = self.tokenizer.tokenize(text)
            result = rules_engine.apply_rules(phrase_type, tokens, text)

            if result and result.get("type") == "fact":
                return self.add_fact(
                    subject=result["subject"],
                    predicate=result["predicate"],
                    obj=result["object"],
                    source=result.get("source")
                )

            logger.debug(f"{LOGGING['prefix_memory']} Не удалось извлечь факт: '{text}'")
            return False
        except Exception as e:
            logger.exception(f"{LOGGING['prefix_memory']} Ошибка при обработке текста: {e}")
            return False
