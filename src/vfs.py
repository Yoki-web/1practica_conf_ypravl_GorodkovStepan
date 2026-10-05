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
