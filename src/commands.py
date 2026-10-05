"""Команды первого этапа практической работы."""


class CommandError(Exception):
    """Ошибка выполнения команды."""


def cmd_ls(vfs, args: list[str]) -> str:
    """Заглушка команды ls."""
    return f"ls: {args} (заглушка)"


def cmd_cd(vfs, args: list[str]) -> str:
    """Заглушка команды cd."""
    return f"cd: {args} (заглушка)"


def cmd_exit(vfs, args: list[str]) -> str:
    """Завершает работу приложения."""
    if args:
        raise CommandError("exit не принимает аргументы")
    raise SystemExit(0)
