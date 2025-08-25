# console.py — Консольный интерфейс Endi-IA v0.0.3

import sys
from config import PROJECT, INTERFACE, LOGGING, SYSTEM, PATHS
from core.common.log import get_logger
from core.processor.parser import Parser
from core.processor.classifier import Classifier
from core.processor.tokenizer import Tokenizer
from core.learner.trainer import Trainer
from core.memory.memory import Memory

logger = get_logger(__name__)

class ConsoleInterface:
    """
    Консольный интерфейс для взаимодействия с Endi-IA.
    Работает в режиме ping-pong диалога.
    """

    def __init__(self):
        self.project_name = PROJECT["name"]
        self.version = PROJECT["version"]

        # Подключаем модули
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.classifier = Classifier()

        # Модуль памяти
        self.memory = Memory(
            memory_path=PATHS["memory_file"],
            knowledge_path=PATHS["memory_file"]
        )

        # Тренер (логика обработки текста и генерации ответа)
        self.trainer = Trainer()

        logger.info(f"{LOGGING['prefix_system']} Консоль инициализирована. Версия: {self.version}")

    def start(self):
        """
        Запуск интерфейса. Бесконечный цикл диалога.
        """
        print(f"=== {self.project_name} v{self.version} ===")
        print("Введите сообщение (или 'exit' для выхода)\n")

        while True:
            try:
                user_input = input("Вы: ").strip()
                if user_input.lower() in ["exit", "quit", "выход"]:
                    print("Выход...")
                    logger.info(f"{LOGGING['prefix_system']} Пользователь завершил сеанс.")
                    break

                if not user_input:
                    continue

                # Обработка текста через Parser и Classifier
                parsed = self.parser.parse(user_input)
                phrase_type = self.classifier.classify(user_input)
                logger.debug(f"{LOGGING['prefix_system']} Классификация: {phrase_type}")

                # Сохраняем факт в памяти (если есть)
                if parsed:
                    self.memory.add_fact_from_text(parsed)

                # Генерация ответа через Trainer
                response = self.trainer.process_text(user_input)

                print(f"{self.project_name}: {response}")
                logger.debug(f"{LOGGING['prefix_system']} Ответ: {response}")

            except (KeyboardInterrupt, EOFError):
                print("\nВыход...")
                logger.info(f"{LOGGING['prefix_system']} Программа завершена вручную.")
                break
            except Exception as e:
                logger.exception(f"{LOGGING['prefix_system']} Ошибка: {e}")
                print(f"[Ошибка] {e}")


# ==========================
# Запуск консоли
# ==========================
if __name__ == "__main__":
    console = ConsoleInterface()
    console.start()
