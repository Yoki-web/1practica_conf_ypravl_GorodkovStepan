"""Команды эмулятора для варианта 6."""

import getpass

from .vfs import VFS


class CommandError(Exception):
    """Ошибка выполнения команды."""


def _check_max_args(args: list[str], maximum: int, usage: str) -> None:
    """Проверяет максимальное количество аргументов."""
    if len(args) > maximum:
        raise CommandError(f"неверные аргументы. Формат: {usage}")


def cmd_ls(vfs: VFS, args: list[str]) -> str:
    """Показывает содержимое виртуального каталога."""
    _check_max_args(args, 1, "ls [путь]")
    target = args[0] if args else "."
    try:
        return "\n".join(vfs.list_directory(target))
    except FileNotFoundError as exc:
        raise CommandError(f"ls: путь не найден: {target}") from exc


def cmd_cd(vfs: VFS, args: list[str]) -> str:
    """Меняет текущий виртуальный каталог."""
    _check_max_args(args, 1, "cd [путь]")
    target = args[0] if args else "/"
    normalized = vfs.normalize(target, vfs.cwd)
    if not vfs.is_directory(normalized):
        raise CommandError(f"cd: каталог не найден: {target}")
    vfs.cwd = normalized
    return ""


def cmd_cat(vfs: VFS, args: list[str]) -> str:
    """Показывает содержимое виртуального файла."""
    if len(args) != 1:
        raise CommandError("неверные аргументы. Формат: cat файл")
    try:
        return vfs.read_file(args[0]).rstrip("\n")
    except FileNotFoundError as exc:
        raise CommandError(f"cat: файл не найден: {args[0]}") from exc


def cmd_tree(vfs: VFS, args: list[str]) -> str:
    """Показывает дерево виртуальной файловой системы."""
    _check_max_args(args, 1, "tree [путь]")
    target = args[0] if args else "."
    try:
        return "\n".join(vfs.tree_lines(target))
    except FileNotFoundError as exc:
        raise CommandError(f"tree: каталог не найден: {target}") from exc


def cmd_whoami(vfs: VFS, args: list[str]) -> str:
    """Возвращает имя пользователя реальной ОС."""
    if args:
        raise CommandError("whoami не принимает аргументы")
    return getpass.getuser()


def cmd_exit(vfs: VFS, args: list[str]) -> str:
    """Завершает работу приложения."""
    if args:
        raise CommandError("exit не принимает аргументы")
    raise SystemExit(0)
