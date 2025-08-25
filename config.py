# config.py — централизованный файл настроек Endi-IA v0.0.3

import os
from datetime import datetime

DEFAULT_LANGUAGE = "ru"  # или "en", в зависимости от проекта


# === 🔗 Вспомогательные функции ===
def resource_path(relative_path: str) -> str:
    """
    Возвращает абсолютный путь относительно корня проекта.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(base_dir, relative_path))


# === ⚙️ ОСНОВНЫЕ НАСТРОЙКИ ПРОЕКТА ===
PROJECT = {
    "name": "Endi-IA",
    "version": "0.0.3",
    "author": "Данил",
    "description": "Интеллектуальная обучаемая система (MVP)",
    "created": datetime.now().strftime("%Y-%m-%d"),
}


# === 📂 ПУТИ И ФАЙЛЫ ===
PATHS = {
    "data_dir": resource_path("data"),
    "memory_file": resource_path("data/memory.json"),
    "curiosity_file": resource_path("data/curiosity.json"),
    "logs_dir": resource_path("data/logs"),
    "meta_log": resource_path("data/logs/meta_log.txt"),
    "config_backup": resource_path("data/config_backup.json"),
    "temp_dir": resource_path("data/temp"),
}


# === 🧠 ПАМЯТЬ (MEMORY) ===
MEMORY = {
    "max_facts": 5000,               # Макс. количество фактов
    "max_fact_length": 500,          # Макс. длина одного факта
    "keyword_sensitivity": 0.75,     # Чувствительность поиска ключевых слов
    "auto_save_interval": 5,         # Автосохранение каждые N запросов
    "compression_enabled": True,     # Сжимать ли старые факты
    "compression_threshold": 0.9,    # Порог важности факта для сжатия
}


# === 🧩 ОБУЧЕНИЕ (LEARNING) ===
LEARNING = {
    "enable_auto_questioning": True, # Генерация вопросов при непонимании
    "min_confidence": 0.6,           # Порог уверенности
    "training_mode": "incremental",  # incremental | batch
    "training_logs": resource_path("data/logs/training_log.txt"),
    "max_questions_per_session": 10, # Ограничение по вопросам за сессию
}


# === 🔍 ОБРАБОТКА (PROCESSOR) ===
PROCESSOR = {
    "max_tokens_per_input": 200,     # Лимит токенов на вход
    "max_tokens_per_response": 300,  # Лимит токенов на выход
    "strict_command_parsing": True,  # Строгий разбор команд
    "enable_fallback": True,         # Запасной ответ при сбое
}


# === 🎨 ИНТЕРФЕЙСЫ ===
INTERFACE = {
    "mode": "console",               # console | gui
    "console_theme": "classic",      # classic | dark | light
    "gui_theme": "dark",
    "show_debug": True,              # Показывать отладочные сообщения
}


# === 📝 ЛОГИРОВАНИЕ ===
LOGGING = {
    "enabled": True,                 # Включены ли логи
    "use_log_module": True,          # Использовать модуль log.py
    "log_level": "DEBUG",            # DEBUG | INFO | WARNING | ERROR
    "max_log_size": 5 * 1024 * 1024, # 5 MB
    "backup_count": 5,
    "log_format": "[%(asctime)s] %(levelname)s: %(message)s",
    "prefix_memory": "[Memory]",     # Префикс для логов памяти
    "prefix_system": "[System]",     # Префикс для системных логов
}


# === 🛠️ СИСТЕМНЫЕ НАСТРОЙКИ ===
SYSTEM = {
    "encoding": "utf-8",
    "autosave_on_exit": True,
    "error_report_file": resource_path("data/logs/errors.log"),
}


# === 🤖 МОДУЛИ ИИ (MVP) ===
MODULES = {
    "enable_memory": True,
    "enable_curiosity": True,
    "enable_processor": True,
    "enable_learning": True,
    "enable_external_ai": False,     # GPT, OpenAI и др.
}


# === 🌐 ВЕБ-СКРАПЕР ===
SCRAPER = {
    "timeout": 10,                   # Таймаут запросов (сек)
    "user_agent": "Endi-IA/0.0.3 (+https://endi.local)",
    "proxies": None,                 # Прокси: {"http": "...", "https": "..."}
    "retry_count": 3,                # Повторные попытки
    "retry_delay": 2,                # Задержка между попытками
}
# === 🧩 NLP НАСТРОЙКИ (для классификатора) ===
QUESTION_STARTERS = [
    "кто", "что", "где", "когда", "почему", "зачем", "как",
    "чей", "который", "сколько", "ли"
]

COMMAND_VERBS = [
    "открой", "запусти", "создай", "удали", "скажи",
    "напиши", "сделай", "покажи", "выведи"
]
# === 📓 НАСТРОЙКИ МЕТА-ЖУРНАЛА ===
META_JOURNAL = {
    "path": PATHS["meta_log"],
    "limit": 500  # Макс. записей в мета-журнале
}
# === 📑 НАСТРОЙКИ SELF-REPORT (самоотчёты ИИ) ===
SELF_REPORT = {
    "path": resource_path("data/logs/self_report.txt"),
    "limit": 300  # Максимум записей в файле самоотчётов
}
CURIOSITY_PATH = PATHS["curiosity_file"]
KNOWLEDGE_PATH = PATHS["memory_file"]