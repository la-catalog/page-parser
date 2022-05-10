import unittest
from pathlib import Path
from unittest import TestCase

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def test_parse(self) -> None:
        parser = Parser()

        for file in Path("tests/rihappy").iterdir():
            text = file.read_text()
            url = f"https://www.rihappy.com.br/{file.name}/p"
            items = parser.parse(text=text, url=url, marketplace="rihappy")

            for item in items:
                print(item)


if __name__ == "__main__":
    unittest.main()
