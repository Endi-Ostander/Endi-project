# GUI.py
import sys
import traceback
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext, messagebox
from core.learner.trainer import Trainer

# --- Скрываем консоль на Windows ---
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass


class _StreamToChat:
    """
    Перехват stdout/stderr в чат.
    Не печатает при выключенном debug_mode.
    Буферизует до перевода строки, чтобы не спамить по символу.
    """
    def __init__(self, app, original_stream, tag):
        self.app = app
        self.original = original_stream
        self.tag = tag
        self.buffer = ""

    def write(self, data):
        try:
            # всегда пишем в оригинал (чтобы не ломать внешние логи)
            self.original.write(data)
            if not self.app.debug_mode:
                return
            self.buffer += data
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                line = line.rstrip()
                if line:
                    color = "#AAAAAA" if self.tag == "LOG" else "#FF5555"
                    self.app._write_chat(f"[{self.tag}]", line, color)
        except Exception:
            # в крайнем случае молча игнорируем, чтобы не уйти в рекурсию
            pass

    def flush(self):
        try:
            self.original.flush()
        except Exception:
            pass


class TkTextLoggingHandler(logging.Handler):
    """logging -> чат"""
    def __init__(self, app):
        super().__init__()
        self.app = app

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.app.debug_mode:
                self.app._write_chat("[LOG]", msg, "#AAAAAA")
        except Exception:
            pass


class EndiGUI:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("Endi-IA v0.02")
        self.root.geometry("1100x720")

        # Core
        self.trainer = Trainer()

        # Debug
        self.debug_mode = False
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = _StreamToChat(self, sys.__stdout__, "LOG")
        sys.stderr = _StreamToChat(self, sys.__stderr__, "ERR")

        # logging -> чат
        self.logger = logging.getLogger("EndiGUI")
        self.logger.setLevel(logging.WARNING)  # по умолчанию не шумим
        self.tk_handler = TkTextLoggingHandler(self)
        self.tk_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        self.logger.addHandler(self.tk_handler)

        # --- Верхняя панель ---
        top = ttk.Frame(root)
        top.pack(fill=X, pady=5, padx=8)

        ttk.Label(top, text="🤖 Endi-IA v0.02", font=("Consolas", 14, "bold")).pack(side=LEFT, padx=5)
        ttk.Button(top, text="Режим отладки", bootstyle="warning", command=self.toggle_debug).pack(side=LEFT, padx=6)
        ttk.Button(top, text="Выход", bootstyle="danger", command=self.exit_program).pack(side=RIGHT, padx=6)

        # --- Вкладки ---
        self.nb = ttk.Notebook(root, bootstyle="dark")
        self.nb.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self._build_tab_chat()
        self._build_tab_memory()
        self._build_tab_questions()
        self._build_tab_journal()
        self._build_tab_goals()
        self._build_tab_logs()

    # ========= ЧАТ =========
    def _build_tab_chat(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="💬 Чат")

        # Чат — разрешаем выделение и копирование, но блокируем ввод с клавиатуры
        self.chat = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 11),
                                              background="#1E1E1E", foreground="#FFFFFF", insertbackground="white")
        self.chat.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.chat.bind("<Key>", lambda e: "break")  # запрет ручного редактирования

        # Панель ввода/кнопок
        bar = ttk.Frame(frame)
        bar.pack(fill=X, padx=10, pady=5)

        self.entry = ttk.Entry(bar, font=("Consolas", 12))
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.entry.bind("<Return>", self.send_message)

        ttk.Button(bar, text="Отправить", bootstyle="success", command=self.send_message).pack(side=LEFT, padx=5)
        ttk.Button(bar, text="Экспорт памяти", bootstyle="info", command=self.export_memory).pack(side=LEFT, padx=5)
        ttk.Button(bar, text="Копировать выделенное", bootstyle="secondary",
                   command=lambda: self._copy_text(self.chat)).pack(side=LEFT, padx=5)

    def send_message(self, _=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self._write_chat("Вы", user_text, "#58A6FF")
        try:
            response = self.trainer.process_text(user_text)
            self._write_chat("Endi", response, "#F28B82")
        except Exception as e:
            error_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self._write_chat("⚠ Ошибка", error_msg, "#FF5555")
            print(error_msg)  # уйдёт в перехват stderr при включённом debug
        finally:
            self.entry.delete(0, "end")

        # обновляем вспомогательные вкладки после каждого запроса
        self._refresh_all_lists()

    def _write_chat(self, sender, text, color):
        self.chat.insert("end", f"{sender}: ", ("bold",))
        self.chat.insert("end", text + "\n", ("color",))
        self.chat.tag_config("bold", font=("Consolas", 11, "bold"))
        self.chat.tag_config("color", foreground=color)
        self.chat.see("end")

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        # переключаем уровень логгера
        self.logger.setLevel(logging.DEBUG if self.debug_mode else logging.WARNING)
        state = "включен" if self.debug_mode else "выключен"
        self._write_chat("[SYSTEM]", f"Режим отладки {state}.", "#AAAAAA")
        messagebox.showinfo("Режим отладки", f"Отладка {state}")

    def export_memory(self):
        try:
            from console import export_memory
            export_memory("md")
            export_memory("csv")
            messagebox.showinfo("Экспорт", "Память сохранена в memory_report.md и memory_report.csv")
        except Exception as e:
            messagebox.showerror("Экспорт", f"Не удалось экспортировать: {e}")

    # ========= ПАМЯТЬ =========
    def _build_tab_memory(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="🧠 Память")

        tools = ttk.Frame(frame)
        tools.pack(fill=X, padx=10, pady=6)

        ttk.Label(tools, text="Поиск:").pack(side=LEFT)
        self.mem_query = tk.StringVar()
        ttk.Entry(tools, textvariable=self.mem_query).pack(side=LEFT, padx=6)
        ttk.Button(tools, text="Обновить", bootstyle="secondary",
                   command=self._mem_refresh).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Копировать выбранные", bootstyle="outline",
                   command=lambda: self._copy_tree(self.mem_tree)).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Удалить выбранные", bootstyle="danger",
                   command=self._mem_delete).pack(side=LEFT, padx=4)

        self.mem_tree = ttk.Treeview(frame, columns=("subject", "predicate", "obj"), show="headings", selectmode="extended")
        for col, title, w in (("subject", "Субъект", 250), ("predicate", "Предикат", 180), ("obj", "Объект", 500)):
            self.mem_tree.heading(col, text=title)
            self.mem_tree.column(col, width=w, anchor="w")
        self.mem_tree.pack(fill=BOTH, expand=True, padx=10, pady=6)

        self._mem_refresh()

    def _mem_refresh(self):
        q = self.mem_query.get().lower().strip()
        for r in self.mem_tree.get_children():
            self.mem_tree.delete(r)
        for f in getattr(self.trainer.memory, "facts", []):
            if not q or q in str(getattr(f, "subject", "")).lower():
                self.mem_tree.insert("", "end", values=(f.subject, f.predicate, f.obj))

    def _mem_delete(self):
        items = self.mem_tree.selection()
        if not items:
            messagebox.showwarning("Удаление", "Выберите строки.")
            return
        removed = 0
        to_delete = []
        for it in items:
            subj, pred, obj = self.mem_tree.item(it)["values"]
            to_delete.append((subj, pred, obj))
        # фильтруем память
        facts = getattr(self.trainer.memory, "facts", [])
        new_facts = [f for f in facts if (f.subject, f.predicate, f.obj) not in to_delete]
        removed = len(facts) - len(new_facts)
        self.trainer.memory.facts = new_facts
        for it in items:
            self.mem_tree.delete(it)
        messagebox.showinfo("Удаление", f"Удалено фактов: {removed}")

    # ========= ВОПРОСЫ =========
    def _build_tab_questions(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="❓ Вопросы")

        tools = ttk.Frame(frame)
        tools.pack(fill=X, padx=10, pady=6)
        ttk.Button(tools, text="Копировать выбранные", bootstyle="outline",
                   command=lambda: self._copy_tree(self.q_tree)).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Удалить выбранные", bootstyle="danger",
                   command=self._q_delete).pack(side=LEFT, padx=4)

        self.q_tree = ttk.Treeview(frame, columns=("question",), show="headings", selectmode="extended")
        self.q_tree.heading("question", text="Вопрос")
        self.q_tree.column("question", width=980, anchor="w")
        self.q_tree.pack(fill=BOTH, expand=True, padx=10, pady=6)

        self._q_refresh()

    def _q_refresh(self):
        for r in self.q_tree.get_children():
            self.q_tree.delete(r)
        for q in getattr(self.trainer.curiosity, "get_questions", lambda: [])():
            self.q_tree.insert("", "end", values=(q,))

    def _q_delete(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showwarning("Удаление", "Выберите строки.")
            return
        removed = 0
        # стараемся удалить из источника
        if hasattr(self.trainer.curiosity, "questions"):
            src = self.trainer.curiosity.questions
            keep = set(v for v in src)
            for it in sel:
                q_text = self.q_tree.item(it)["values"][0]
                if q_text in keep:
                    keep.discard(q_text)
                    removed += 1
            self.trainer.curiosity.questions = list(keep)
        # удаляем из UI
        for it in sel:
            self.q_tree.delete(it)
        messagebox.showinfo("Удаление", f"Удалено вопросов: {removed}")

    # ========= ЖУРНАЛ =========
    def _build_tab_journal(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="📜 Журнал")

        tools = ttk.Frame(frame)
        tools.pack(fill=X, padx=10, pady=6)
        ttk.Button(tools, text="Копировать выделенное", bootstyle="outline",
                   command=lambda: self._copy_text(self.journal)).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Удалить выделенные строки", bootstyle="danger",
                   command=self._journal_delete_selected_lines).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Обновить", bootstyle="secondary",
                   command=self._journal_refresh).pack(side=LEFT, padx=4)

        self.journal = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 11),
                                                 background="#1E1E1E", foreground="#FFFFFF", insertbackground="white")
        self.journal.pack(fill=BOTH, expand=True, padx=10, pady=6)
        self.journal.bind("<Key>", lambda e: "break")  # запрет редактирования
        self._journal_refresh()

    def _journal_refresh(self):
        self.journal.config(state="normal")
        self.journal.delete("1.0", "end")
        lines = []
        try:
            lines = list(getattr(self.trainer.journal, "get_recent_entries", lambda *a, **k: [])(200))
        except Exception:
            pass
        for ln in lines:
            self.journal.insert("end", f"{ln.rstrip()}\n")
        self.journal.see("end")

    def _journal_delete_selected_lines(self):
        try:
            # получаем выделение; если нет, предупреждаем
            try:
                start = self.journal.index("sel.first")
                end = self.journal.index("sel.last")
            except tk.TclError:
                messagebox.showwarning("Удаление", "Выделите строки в журнале.")
                return

            # вычисляем целые строки для удаления
            line_start = f"{start.split('.')[0]}.0"
            line_end = f"{end.split('.')[0]}.end"

            text_to_delete = self.journal.get(line_start, line_end).splitlines()
            # пытаемся удалить из источника, если доступны внутренние структуры
            removed = 0
            # Часто хранятся как self.trainer.journal.entries или list
            for attr in ("entries", "logs", "journal", "_entries"):
                if hasattr(self.trainer.journal, attr):
                    lst = list(getattr(self.trainer.journal, attr))
                    new_lst = [x for x in lst if str(x).rstrip() not in text_to_delete]
                    removed = len(lst) - len(new_lst)
                    try:
                        setattr(self.trainer.journal, attr, new_lst)
                        break
                    except Exception:
                        pass
            # если есть метод delete/remove — пробуем им
            for mname in ("delete_entry", "remove_entry", "remove"):
                if hasattr(self.trainer.journal, mname):
                    for t in text_to_delete:
                        try:
                            getattr(self.trainer.journal, mname)(t)
                            removed += 1
                        except Exception:
                            pass

            # чистим UI
            self.journal.delete(line_start, line_end)
            messagebox.showinfo("Журнал", f"Удалено строк (по возможности и из источника): {removed}")
        except Exception as e:
            messagebox.showerror("Журнал", f"Ошибка удаления: {e}")

    # ========= ЦЕЛИ =========
    def _build_tab_goals(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="🎯 Цели")

        tools = ttk.Frame(frame)
        tools.pack(fill=X, padx=10, pady=6)
        ttk.Button(tools, text="Копировать выбранные", bootstyle="outline",
                   command=lambda: self._copy_tree(self.goals_tree)).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Удалить выбранные", bootstyle="danger",
                   command=self._goals_delete).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Обновить", bootstyle="secondary",
                   command=self._goals_refresh).pack(side=LEFT, padx=4)

        self.goals_tree = ttk.Treeview(frame, columns=("goal",), show="headings", selectmode="extended")
        self.goals_tree.heading("goal", text="Цель")
        self.goals_tree.column("goal", width=980, anchor="w")
        self.goals_tree.pack(fill=BOTH, expand=True, padx=10, pady=6)

        self._goals_refresh()

    def _goals_refresh(self):
        for r in self.goals_tree.get_children():
            self.goals_tree.delete(r)
        goals = []
        try:
            goals = list(getattr(self.trainer.journal, "get_logged_goals", lambda: [])())
        except Exception:
            pass
        for g in goals:
            self.goals_tree.insert("", "end", values=(g,))

    def _goals_delete(self):
        sel = self.goals_tree.selection()
        if not sel:
            messagebox.showwarning("Удаление", "Выберите цели.")
            return
        removed = 0
        texts = [self.goals_tree.item(it)["values"][0] for it in sel]

        # пробуем удалить из источника
        # популярные варианты хранения: trainer.journal.goals / logged_goals / _goals
        for attr in ("goals", "logged_goals", "_goals"):
            if hasattr(self.trainer.journal, attr):
                lst = list(getattr(self.trainer.journal, attr))
                new_lst = [x for x in lst if str(x) not in texts]
                removed = len(lst) - len(new_lst)
                try:
                    setattr(self.trainer.journal, attr, new_lst)
                    break
                except Exception:
                    pass

        # пробуем метод
        for mname in ("remove_goal", "delete_goal", "remove"):
            if hasattr(self.trainer.journal, mname):
                for t in texts:
                    try:
                        getattr(self.trainer.journal, mname)(t)
                        removed += 1
                    except Exception:
                        pass

        for it in sel:
            self.goals_tree.delete(it)
        messagebox.showinfo("Цели", f"Удалено целей (насколько позволили API): {removed}")

    # ========= ЛОГ =========
    def _build_tab_logs(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="📝 Лог")

        tools = ttk.Frame(frame)
        tools.pack(fill=X, padx=10, pady=6)
        ttk.Button(tools, text="Копировать выделенное", bootstyle="outline",
                   command=lambda: self._copy_text(self.logs)).pack(side=LEFT, padx=4)
        ttk.Button(tools, text="Обновить", bootstyle="secondary",
                   command=self._logs_refresh).pack(side=LEFT, padx=4)

        self.logs = scrolledtext.ScrolledText(frame, wrap="word", font=("Consolas", 11),
                                              background="#1E1E1E", foreground="#FFFFFF", insertbackground="white")
        self.logs.pack(fill=BOTH, expand=True, padx=10, pady=6)
        self.logs.bind("<Key>", lambda e: "break")
        self._logs_refresh()

    def _logs_refresh(self):
        self.logs.config(state="normal")
        self.logs.delete("1.0", "end")
        lines = []
        try:
            lines = list(getattr(self.trainer.reporter, "get_recent_logs", lambda *a, **k: [])())
        except Exception:
            pass
        for ln in lines:
            self.logs.insert("end", f"{str(ln).rstrip()}\n")
        self.logs.see("end")

    # ========= Общие утилиты =========
    def _copy_text(self, text_widget: scrolledtext.ScrolledText):
        """Копирует выделенный текст; если выделения нет — копирует всё."""
        try:
            # эти виджеты 'read-only' только для ввода; чтение/выделение разрешено
            try:
                data = text_widget.get("sel.first", "sel.last")
            except tk.TclError:
                data = text_widget.get("1.0", "end-1c")
            if not data:
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(data)
            messagebox.showinfo("Копирование", "Текст скопирован в буфер обмена.")
        except Exception as e:
            messagebox.showerror("Копирование", f"Не удалось скопировать: {e}")

    def _copy_tree(self, tree: ttk.Treeview):
        """Копирует выбранные строки из Treeview (или все, если ничего не выбрано)."""
        items = tree.selection()
        if not items:
            items = tree.get_children()
            if not items:
                return
        lines = []
        cols = tree["columns"]
        for it in items:
            vals = tree.item(it)["values"]
            # склеиваем значения человекочитаемо
            line = " — ".join(str(v) for v in vals)
            lines.append(line)
        data = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(data)
        messagebox.showinfo("Копирование", "Строки скопированы в буфер обмена.")

    def _refresh_all_lists(self):
        self._mem_refresh()
        self._q_refresh()
        self._journal_refresh()
        self._goals_refresh()
        self._logs_refresh()

    def exit_program(self):
        # возвращаем потоки
        try:
            sys.stdout = self._orig_stdout
            sys.stderr = self._orig_stderr
        except Exception:
            pass
        self.root.quit()


if __name__ == "__main__":
    # Глобальная тема на всё окно (в т.ч. бордеры ttk)
    root = ttk.Window(themename="darkly")
    EndiGUI(root)
    root.mainloop()
