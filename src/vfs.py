"""Виртуальная файловая система, загружаемая из ZIP в память."""

from __future__ import annotations

import base64
import posixpath
import zipfile
from dataclasses import dataclass
from pathlib import Path


class VFSLoadError(Exception):
    """Ошибка загрузки виртуальной файловой системы."""


@dataclass
class StoredFile:
    """Данные виртуального файла."""

    data: str
    encoding: str


class VFS:
    """VFS, состояние которой хранится только в оперативной памяти."""

    def __init__(self, name: str = "vfs"):
        self.name = name
        self.cwd = "/"
        self.directories = {"/"}
        self.files: dict[str, StoredFile] = {}

    def load_from_zip(self, path: str) -> None:
        """Загружает ZIP без распаковки его содержимого на диск."""
        source = Path(path)
        if not source.is_file():
            raise VFSLoadError(f"файл VFS не найден: {path}")
        if not zipfile.is_zipfile(source):
            raise VFSLoadError(f"неверный формат VFS: {path}")
        self.name = source.name
        self.cwd = "/"
        self.directories = {"/"}
        self.files = {}
        try:
            with zipfile.ZipFile(source, "r") as archive:
                for info in archive.infolist():
                    self._load_member(archive, info)
        except (OSError, zipfile.BadZipFile) as exc:
            raise VFSLoadError(str(exc)) from exc

    def _load_member(self, archive: zipfile.ZipFile, info) -> None:
        """Добавляет один элемент ZIP в структуру VFS."""
        path = self.normalize("/" + info.filename)
        self._add_parents(path)
        if info.is_dir():
            self.directories.add(path)
            return
        raw = archive.read(info.filename)
        self.files[path] = self._store_data(raw)

    @staticmethod
    def _store_data(raw: bytes) -> StoredFile:
        """Текст хранит как UTF-8, а двоичные данные как base64."""
        try:
            return StoredFile(raw.decode("utf-8"), "utf-8")
        except UnicodeDecodeError:
            data = base64.b64encode(raw).decode("ascii")
            return StoredFile(data, "base64")

    def _add_parents(self, path: str) -> None:
        """Добавляет родительские каталоги заданного пути."""
        current = posixpath.dirname(path)
        while current and current != "/":
            self.directories.add(current)
            current = posixpath.dirname(current)
        self.directories.add("/")

    @staticmethod
    def normalize(path: str, current: str = "/") -> str:
        """Приводит виртуальный путь к абсолютному POSIX-виду."""
        if not path.startswith("/"):
            path = posixpath.join(current, path)
        normalized = posixpath.normpath(path)
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        return normalized

    def is_directory(self, path: str) -> bool:
        """Проверяет, является ли путь каталогом VFS."""
        target = self.normalize(path, self.cwd)
        return target in self.directories

    def list_directory(self, path: str = ".") -> list[str]:
        """Возвращает непосредственное содержимое каталога."""
        base = self.normalize(path, self.cwd)
        if base not in self.directories:
            raise FileNotFoundError(base)
        prefix = "/" if base == "/" else base + "/"
        result = set()
        all_paths = self.directories | set(self.files)
        for item in all_paths:
            if item == base or not item.startswith(prefix):
                continue
            rest = item[len(prefix):]
            if rest:
                result.add(rest.split("/", 1)[0])
        return sorted(result)

    def read_file(self, path: str) -> str:
        """Читает виртуальный файл из памяти."""
        target = self.normalize(path, self.cwd)
        if target not in self.files:
            raise FileNotFoundError(target)
        stored = self.files[target]
        if stored.encoding == "base64":
            return f"[base64] {stored.data}"
        return stored.data

    def tree_lines(self, path: str = ".") -> list[str]:
        """Строит строки дерева для выбранного каталога."""
        base = self.normalize(path, self.cwd)
        if base not in self.directories:
            raise FileNotFoundError(base)
        lines = [base]
        self._walk_tree(base, "", lines)
        return lines

    def _walk_tree(self, base: str, prefix: str, lines: list[str]) -> None:
        """Рекурсивно добавляет элементы каталога в дерево."""
        children = self._children_for(base)
        last_index = len(children) - 1
        for index, name in enumerate(children):
            is_last = index == last_index
            branch = "└── " if is_last else "├── "
            lines.append(prefix + branch + name)
            child = self.normalize(name, base)
            if child in self.directories:
                extra = "    " if is_last else "│   "
                self._walk_tree(child, prefix + extra, lines)

    def _children_for(self, base: str) -> list[str]:
        """Возвращает детей абсолютного каталога."""
        old_cwd = self.cwd
        try:
            self.cwd = base
            return self.list_directory(".")
        finally:
            self.cwd = old_cwd

    def move(self, source: str, destination: str) -> None:
        """Перемещает файл или каталог только в памяти."""
        src = self.normalize(source, self.cwd)
        dst = self.normalize(destination, self.cwd)
        if src in self.files:
            self._move_file(src, dst)
            return
        if src in self.directories and src != "/":
            self._move_directory(src, dst)
            return
        raise FileNotFoundError(src)

    def _move_file(self, source: str, destination: str) -> None:
        """Перемещает или переименовывает один виртуальный файл."""
        if destination in self.directories:
            name = posixpath.basename(source)
            destination = self.normalize(name, destination)
        self._add_parents(destination)
        self.files[destination] = self.files.pop(source)

    def _move_directory(self, source: str, destination: str) -> None:
        """Перемещает каталог и все его дочерние элементы."""
        if destination in self.directories:
            name = posixpath.basename(source)
            destination = self.normalize(name, destination)
        dir_changes = self._directory_changes(source, destination)
        file_changes = self._file_changes(source, destination)
        for old, new in dir_changes.items():
            self.directories.discard(old)
            self.directories.add(new)
        for old, new in file_changes.items():
            self.files[new] = self.files.pop(old)
        self._add_parents(destination)
        if self.cwd == source or self.cwd.startswith(source + "/"):
            self.cwd = destination + self.cwd[len(source):]

    def _directory_changes(
        self,
        source: str,
        destination: str,
    ) -> dict[str, str]:
        """Строит новые пути каталогов после mv."""
        changes = {}
        for path in list(self.directories):
            if path == source or path.startswith(source + "/"):
                changes[path] = destination + path[len(source):]
        return changes

    def _file_changes(
        self,
        source: str,
        destination: str,
    ) -> dict[str, str]:
        """Строит новые пути файлов после mv каталога."""
        changes = {}
        for path in list(self.files):
            if path.startswith(source + "/"):
                changes[path] = destination + path[len(source):]
        return changes
