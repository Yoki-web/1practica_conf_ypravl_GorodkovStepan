"""GUI-эмулятор командной оболочки, вариант 6."""

import argparse
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext

from . import commands
from .parser import ParseError, parse
from .vfs import VFS


HANDLERS = {
    "ls": commands.cmd_ls,
    "cd": commands.cmd_cd,
    "exit": commands.cmd_exit,
}


def get_handler(name: str):
    """Возвращает обработчик команды по ее имени."""
    return HANDLERS.get(name)


def parse_args() -> argparse.Namespace:
    """Читает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", help="Путь к ZIP-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    return parser.parse_args()


class ShellEmulator:
    """Окно эмулятора с вводом и выводом команд."""

    def __init__(self, root: tk.Tk, vfs: VFS, args: argparse.Namespace):
        self.root = root
        self.vfs = vfs
        self.args = args
        root.title(f"VFS: {vfs.name}")
        root.geometry("800x500")
        self.output = scrolledtext.ScrolledText(root, font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.entry = tk.Entry(root, font=("Consolas", 11))
        self.entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()
        self._show_args()

    def _print(self, text: str) -> None:
        """Добавляет строку в поле вывода."""
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def _show_args(self) -> None:
        """Показывает параметры запуска для отладки."""
        self._print("Параметры запуска:")
        self._print(f"VFS: {self.args.vfs}")
        self._print(f"Скрипт: {self.args.script}")
        self._print("")

    def _on_enter(self, event=None) -> None:
        """Обрабатывает команду из поля ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_line(line)

    def run_line(self, line: str) -> bool:
        """Показывает и выполняет одну команду."""
        self._print(f"{self.vfs.name}:{self.vfs.cwd}$ {line}")
        try:
            name, args = parse(line)
            handler = get_handler(name)
            if handler is None:
                raise commands.CommandError(
                    f"неизвестная команда '{name}'"
                )
            result = handler(self.vfs, args)
            if result:
                self._print(result)
        except (ParseError, commands.CommandError) as exc:
            self._print(f"Ошибка: {exc}")
        except SystemExit:
            self.root.destroy()
            return False
        return True

    def run_startup_script(self) -> None:
        """Выполняет стартовый скрипт и пропускает комментарии."""
        if not self.args.script:
            return
        try:
            lines = Path(self.args.script).read_text(
                encoding="utf-8"
            ).splitlines()
        except OSError as exc:
            self._print(f"Ошибка стартового скрипта: {exc}")
            return
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if not self.run_line(line):
                break


def main() -> None:
    """Запускает GUI с параметрами конфигурации."""
    args = parse_args()
    root = tk.Tk()
    app = ShellEmulator(root, VFS(), args)
    root.after(0, app.run_startup_script)
    root.mainloop()


if __name__ == "__main__":
    main()
