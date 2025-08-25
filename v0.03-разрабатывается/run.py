from core.learner.trainer import Trainer
import sys

# Для вывода можно импортировать отдельно функции из dev_console_ext, 
# но лучше вынести их в отдельный утилитный модуль, чтобы избежать циклов.

def main():
    trainer = Trainer()
    print("Введите текст для обучения ИИ (команды начинаются с /, exit — выход):")

    while True:
        user_input = input("> ").strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input[1:].split()
            cmd = parts[0].lower()

            if cmd == "exit":
                break
            elif cmd == "mem":
                if len(parts) == 1:
                    print("❗ Уточните: facts, knowledge или export")
                    continue
                subcmd = parts[1].lower()

                if subcmd == "facts":
                    subj = parts[2] if len(parts) > 2 else None
                    # Вывод фактов — здесь вызывай функцию из console или отдельно
                    print(f"Вывести факты для: {subj or 'все'} (реализуй логику отдельно)")
                elif subcmd == "knowledge":
                    tag = parts[2] if len(parts) > 2 else None
                    print(f"Вывести знания для тега: {tag or 'все'} (реализуй логику отдельно)")
                elif subcmd == "export":
                    if len(parts) < 3:
                        print("❗ Укажите формат: md или csv")
                    elif parts[2] == "md":
                        print("Экспорт в md (реализуй логику отдельно)")
                    elif parts[2] == "csv":
                        print("Экспорт в csv (реализуй логику отдельно)")
                    else:
                        print("❗ Неизвестный формат. Используйте md или csv.")
                else:
                    print(f"❗ Неизвестная команда: {subcmd}")
            else:
                print(f"❗ Неизвестная команда: /{cmd}")
        else:
            trainer.process_text(user_input)

if __name__ == "__main__":
    main()
