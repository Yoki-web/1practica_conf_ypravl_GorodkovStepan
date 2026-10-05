"""Тесты основных команд варианта 6."""

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from src import commands
from src.vfs import VFS


class CommandTests(unittest.TestCase):
    """Проверяет ls, cd, cat и tree на VFS."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        path = Path(self.temp_dir.name) / "test.zip"
        with ZipFile(path, "w") as archive:
            archive.writestr("a/file.txt", "hello\n")
            archive.writestr("a/b/deep.txt", "deep\n")
        self.vfs = VFS()
        self.vfs.load_from_zip(str(path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ls_and_cd(self):
        self.assertEqual(commands.cmd_ls(self.vfs, []), "a")
        commands.cmd_cd(self.vfs, ["a"])
        self.assertEqual(self.vfs.cwd, "/a")
        self.assertEqual(commands.cmd_ls(self.vfs, []), "b\nfile.txt")

    def test_cat(self):
        result = commands.cmd_cat(self.vfs, ["a/file.txt"])
        self.assertEqual(result, "hello")

    def test_tree(self):
        result = commands.cmd_tree(self.vfs, ["/"])
        self.assertIn("deep.txt", result)


if __name__ == "__main__":
    unittest.main()
