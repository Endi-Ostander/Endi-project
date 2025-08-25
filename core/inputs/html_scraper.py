# core/inputs/html_scraper.py — HTML-скрейпер v0.0.3
import time
import requests
from bs4 import BeautifulSoup
from core.common.log import log_error, log_debug
from config import SCRAPER


class HtmlScraper:
    """
    Модуль для получения текста с HTML-страниц.
    v0.0.3:
    - Берёт настройки из SCRAPER
    - Поддержка прокси
    - Повторные попытки при ошибке
    """

    def __init__(self):
        self.timeout = SCRAPER.get("timeout", 10)
        self.headers = {"User-Agent": SCRAPER.get("user_agent", "Endi-IA/0.0.3")}
        self.proxies = SCRAPER.get("proxies", None)
        self.retry_count = SCRAPER.get("retry_count", 3)
        self.retry_delay = SCRAPER.get("retry_delay", 2)

    def fetch_text(self, url: str) -> str:
        """
        Загружает страницу по URL и возвращает текст из <body>.
        Делает несколько попыток при ошибке.
        """
        log_debug(f"[HtmlScraper] Запрос к URL: {url}")

        for attempt in range(1, self.retry_count + 1):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    proxies=self.proxies
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                body = soup.body
                text = body.get_text(separator=' ', strip=True) if body else ""

                log_debug(f"[HtmlScraper] Успешно загружено {len(text)} символов.")
                return text

            except requests.exceptions.RequestException as e:
                log_error(f"[HtmlScraper] Попытка {attempt}/{self.retry_count} не удалась: {e}")
                if attempt < self.retry_count:
                    log_debug(f"[HtmlScraper] Повторная попытка через {self.retry_delay} сек...")
                    time.sleep(self.retry_delay)
            except Exception as e:
                log_error(f"[HtmlScraper] Неожиданная ошибка: {e}")
                break

        log_error(f"[HtmlScraper] Все {self.retry_count} попыток не удались.")
        return ""
