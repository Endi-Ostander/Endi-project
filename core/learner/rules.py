# core/learner/rules.py — Правила интерпретации фраз v0.0.3
from typing import List, Optional, Dict, Any
from core.common.types import PhraseType
from core.common.log import get_logger
from config import LOGGING

logger = get_logger(__name__)

class Rule:
    def __init__(self, name: str, condition: callable, action: callable):
        self.name = name
        self.condition = condition
        self.action = action

class RulesEngine:
    def __init__(self):
        self.rules: List[Rule] = []
        logger.debug(f"{LOGGING['prefix_system']} RulesEngine инициализирован.")

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        logger.debug(f"{LOGGING['prefix_system']} Добавлено правило: {rule.name}")

    def apply_rules(self, phrase_type: PhraseType, tokens: List[str], raw_text: str) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule.condition(phrase_type, tokens, raw_text):
                logger.debug(f"{LOGGING['prefix_system']} Применено правило: {rule.name}")
                return rule.action(phrase_type, tokens, raw_text)
        return None

# Базовые правила
def condition_fact_long(phrase_type: PhraseType, tokens: List[str], raw_text: str) -> bool:
    return phrase_type == PhraseType.STATEMENT and len(tokens) >= 3

def action_fact_long(phrase_type: PhraseType, tokens: List[str], raw_text: str) -> Dict[str, Any]:
    return {"type": "fact", "subject": tokens[0], "predicate": tokens[1], "object": " ".join(tokens[2:]), "source": raw_text}

def condition_fact_short(phrase_type: PhraseType, tokens: List[str], raw_text: str) -> bool:
    return phrase_type == PhraseType.STATEMENT and len(tokens) == 2

def action_fact_short(phrase_type: PhraseType, tokens: List[str], raw_text: str) -> Dict[str, Any]:
    return {"type": "fact", "subject": tokens[0], "predicate": tokens[1], "object": "", "source": raw_text}

def condition_question(phrase_type, tokens, raw_text):
    return phrase_type == PhraseType.QUESTION

def action_question(phrase_type, tokens, raw_text):
    return {"type": "question", "text": raw_text, "tokens": tokens}

# Инициализация
rules_engine = RulesEngine()
rules_engine.add_rule(Rule("fact_rule_long", condition_fact_long, action_fact_long))
rules_engine.add_rule(Rule("fact_rule_short", condition_fact_short, action_fact_short))
rules_engine.add_rule(Rule("question_rule", condition_question, action_question))
