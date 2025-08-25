# core/inputs/text_input.py — Консольный ввод v0.0.3
from core.common.log import log_debug


class TextInput:
    """
    Модуль получения текстового ввода от пользователя.
    v0.0.3: добавлен логгер для отладки, подготовка к расширяемости.
    """

    def get_input(self) -> str:
        """
        Получает текстовую строку от пользователя (через консоль).
        """
        log_debug("[TextInput] Ожидание ввода пользователя...")
        return input("Введите текст для Endi: ")
