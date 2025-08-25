# core/common/log.py — Логирование v0.0.3
import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOGGING, PATHS

# === 🔧 Настройка основного логгера проекта ===

LOG_FILE = os.path.join(PATHS["logs_dir"], "endi.log")
os.makedirs(PATHS["logs_dir"], exist_ok=True)

# Создаём хэндлер с ротацией логов
handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOGGING.get("max_log_size", 5 * 1024 * 1024),  # 5 MB
    backupCount=LOGGING.get("backup_count", 5),
    encoding="utf-8"
)

# Настройка форматтера
formatter = logging.Formatter(LOGGING.get("log_format", "[%(asctime)s] %(levelname)s: %(message)s"))
handler.setFormatter(formatter)

# Основной логгер
base_logger = logging.getLogger("EndiLogger")
base_logger.setLevel(getattr(logging, LOGGING.get("log_level", "DEBUG")))
base_logger.addHandler(handler)
base_logger.propagate = False


# === 🔹 Утилиты для быстрого логирования ===
def log_info(message: str):
    """Запись информационного сообщения."""
    base_logger.info(message)


def log_error(message: str):
    """Запись ошибки."""
    base_logger.error(message)


def log_debug(message: str):
    """Запись отладочного сообщения."""
    base_logger.debug(message)


# === 🔹 Универсальный метод получения логгера ===
def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер для модуля по имени.
    Все логгеры используют общую настройку и ротацию.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # Чтобы не дублировать хендлеры
        logger.setLevel(base_logger.level)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
