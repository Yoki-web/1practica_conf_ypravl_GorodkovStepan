"""Парсер командной строки для эмулятора."""

import shlex


class ParseError(Exception):
    """Ошибка разбора введенной команды."""


def parse(line: str) -> tuple[str, list[str]]:
    """Разделяет строку на имя команды и аргументы."""
    if not line.strip():
        raise ParseError("пустая команда")
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        raise ParseError("неверно расставлены кавычки") from exc
    if not parts:
        raise ParseError("пустая команда")
    return parts[0], parts[1:]
