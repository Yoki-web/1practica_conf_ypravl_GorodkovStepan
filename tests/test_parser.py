"""Тесты парсера первого этапа."""

import unittest

from src.parser import ParseError, parse


class ParserTests(unittest.TestCase):
    """Проверяет разбор обычных и кавычечных аргументов."""

    def test_quotes(self):
        name, args = parse('cd "folder with spaces"')
        self.assertEqual(name, "cd")
        self.assertEqual(args, ["folder with spaces"])

    def test_bad_quotes(self):
        with self.assertRaises(ParseError):
            parse('cd "folder')


if __name__ == "__main__":
    unittest.main()
