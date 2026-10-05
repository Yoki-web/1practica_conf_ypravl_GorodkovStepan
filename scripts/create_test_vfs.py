"""Создает тестовые ZIP-архивы для проверки VFS варианта 6."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
VFS_DIR = ROOT / "vfs"


def make_zip(name: str, files: dict[str, bytes]) -> None:
    """Создает один тестовый ZIP с заданными файлами."""
    VFS_DIR.mkdir(exist_ok=True)
    path = VFS_DIR / name
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for filename, data in files.items():
            archive.writestr(filename, data)


def main() -> None:
    """Создает минимальную, обычную и глубокую VFS."""
    make_zip("minimal.zip", {"hello.txt": b"hello\n"})
    make_zip(
        "few_files.zip",
        {
            "readme.txt": b"test vfs\n",
            "docs/info.txt": b"docs\n",
            "data.bin": bytes([0, 255, 1, 254]),
        },
    )
    make_zip(
        "deep.zip",
        {
            "root.txt": b"root file\n",
            "level1/notes.txt": b"level one\n",
            "level1/level2/info.txt": b"level two\n",
            "level1/level2/level3/deep.txt": b"deep file\n",
        },
    )
    print("Тестовые VFS созданы в папке vfs")


if __name__ == "__main__":
    main()
