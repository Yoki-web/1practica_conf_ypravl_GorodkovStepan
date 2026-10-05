"""Минимальное состояние VFS для первого этапа."""


class VFS:
    """Состояние виртуальной файловой системы."""

    def __init__(self, name: str = "vfs"):
        self.name = name
        self.cwd = "/"
