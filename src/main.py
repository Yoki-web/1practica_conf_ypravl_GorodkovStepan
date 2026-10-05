"""GUI-эмулятор командной оболочки, вариант 6."""

import tkinter as tk
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


class ShellEmulator:
    """Окно эмулятора с вводом и выводом команд."""

    def __init__(self, root: tk.Tk, vfs: VFS):
        self.root = root
        self.vfs = vfs
        root.title(f"VFS: {vfs.name}")
        root.geometry("800x500")
        self.output = scrolledtext.ScrolledText(root, font=("Consolas", 11))
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.entry = tk.Entry(root, font=("Consolas", 11))
        self.entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _print(self, text: str) -> None:
        """Добавляет строку в поле вывода."""
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def _on_enter(self, event=None) -> None:
        """Обрабатывает команду из поля ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self._print(f"{self.vfs.name}:{self.vfs.cwd}$ {line}")
        self._execute(line)

    def _execute(self, line: str) -> None:
        """Разбирает и выполняет одну команду."""
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


def main() -> None:
    """Запускает первый этап GUI-эмулятора."""
    root = tk.Tk()
    ShellEmulator(root, VFS())
    root.mainloop()


if __name__ == "__main__":
    main()
