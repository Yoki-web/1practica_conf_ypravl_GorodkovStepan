"""Тесты загрузки VFS из ZIP."""

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from src.vfs import VFS, VFSLoadError


class VFSTests(unittest.TestCase):
    """Проверяет загрузку ZIP и обработку ошибок."""

    def test_load_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("a/b.txt", "hello")
            vfs = VFS()
            vfs.load_from_zip(str(path))
            self.assertIn("/a", vfs.directories)
            self.assertIn("/a/b.txt", vfs.files)

    def test_missing_zip(self):
        with self.assertRaises(VFSLoadError):
            VFS().load_from_zip("missing.zip")


if __name__ == "__main__":
    unittest.main()
