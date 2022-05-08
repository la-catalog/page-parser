import unittest
from pathlib import Path
from unittest import TestCase

from structlog.stdlib import get_logger

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def test_parse(self) -> None:
        parser = Parser(get_logger())

        for file in Path("tests/rihappy").iterdir():
            text = file.read_text()
            parser.parse(text, "", "rihappy")


if __name__ == "__main__":
    unittest.main()
