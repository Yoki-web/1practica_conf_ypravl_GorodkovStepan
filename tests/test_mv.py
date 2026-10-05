"""Тест команды mv для варианта 6."""

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from src import commands
from src.vfs import VFS


class MoveTests(unittest.TestCase):
    """Проверяет переименование и перемещение только в памяти."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "test.zip"
        with ZipFile(self.path, "w") as archive:
            archive.writestr("file.txt", "hello")
            archive.writestr("dir/inside.txt", "inside")
        self.vfs = VFS()
        self.vfs.load_from_zip(str(self.path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_rename_file_in_memory(self):
        commands.cmd_mv(self.vfs, ["file.txt", "renamed.txt"])
        self.assertIn("/renamed.txt", self.vfs.files)
        self.assertNotIn("/file.txt", self.vfs.files)
        with ZipFile(self.path, "r") as archive:
            self.assertIn("file.txt", archive.namelist())
            self.assertNotIn("renamed.txt", archive.namelist())

    def test_move_file_to_directory(self):
        commands.cmd_mv(self.vfs, ["file.txt", "dir"])
        self.assertIn("/dir/file.txt", self.vfs.files)


if __name__ == "__main__":
    unittest.main()
