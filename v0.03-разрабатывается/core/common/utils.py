# core/common/utils.py — Утилиты v0.0.3
import json
import os
import re
import uuid
from typing import List, Dict
from datetime import datetime, timezone
from config import PATHS


def resource_path(relative_path: str) -> str:
    """
    Абсолютный путь относительно project_root.
    Работает, даже если скрипт запущен из поддиректории.
    """
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    return os.path.normpath(os.path.join(base_path, relative_path))


def clean_text(text: str) -> str:
    """
    Очистка текста:
    - нормализует тире и слэши
    - убирает повторяющиеся символы
    - удаляет всё кроме букв, цифр, дефиса и пробелов
    - приводит к нижнему регистру
    """
    text = text.replace('—', '-').replace('–', '-').replace('―', '-').replace('/', '-')
    text = re.sub(r'-{2,}', '-', text)
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'\s+', ' ', text).strip().lower()


def normalize_whitespace(text: str) -> str:
    """Приводит все пробелы к одному."""
    return re.sub(r'\s+', ' ', text).strip()


def is_ignorable(text: str) -> bool:
    """
    Определяет, является ли текст командой (/help),
    пустым или техническим вводом (> prompt).
    """
    text = text.strip()
    return not text or text.startswith("/") or text.startswith(">")


def generate_id() -> str:
    """Создаёт уникальный идентификатор."""
    return str(uuid.uuid4())


def timestamp() -> str:
    """Возвращает текущую дату и время в ISO формате (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def load_json(filepath: str) -> Dict:
    """Загружает JSON-файл в словарь."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath: str, data: Dict) -> None:
    """Сохраняет словарь в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def pretty_print(obj: Dict):
    """Удобный вывод словаря."""
    print(json.dumps(obj, indent=4, ensure_ascii=False))


def is_valid_statement(tokens: List[str]) -> bool:
    """
    Проверка: можно ли считать утверждение осмысленным.
    Требуется хотя бы 2 слова и связка.
    """
    if len(tokens) < 2:
        return False
    linking_words = {"это", "есть", "-", "—", "является", "было", "будет", "стала", "была"}
    return any(t in linking_words for t in tokens)
