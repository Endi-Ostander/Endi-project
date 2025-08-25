# core/thinker/self_report.py — Самоотчёт ИИ v0.0.3
# core/thinker/self_report.py — Самоотчёты ИИ v0.0.3
import os
from core.common.utils import timestamp
from core.common.log import get_logger
from config import LOGGING, SELF_REPORT

logger = get_logger(__name__)

class SelfReporter:
    """
    Логирует действия и события ИИ для самоанализа.
    """
    def __init__(self, log_path: str = None):
        self.log_path = log_path or SELF_REPORT["path"]
        self.limit = SELF_REPORT.get("limit", 300)  # Максимум строк при чтении
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        logger.debug(f"{LOGGING['prefix_system']} SelfReporter инициализирован. Путь: {self.log_path}")

    def log_action(self, action: str, source: str = "Trainer"):
        entry = f"[{timestamp()}] [{source}] {action}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(entry)
            logger.debug(f"{LOGGING['prefix_system']} Лог: {action}")
        except IOError as e:
            logger.error(f"{LOGGING['prefix_system']} Ошибка записи лога: {e}")

    def get_recent_logs(self, limit: int = None) -> list[str]:
        """
        Возвращает последние записи самоотчёта.
        """
        limit = limit or self.limit
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return f.readlines()[-limit:]

    def describe(self) -> str:
        return "Я фиксирую события и действия ИИ для анализа."
