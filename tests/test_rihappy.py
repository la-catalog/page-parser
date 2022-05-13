import unittest
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def test_parse(self) -> None:
        parser = Parser()

        for file in Path("tests/rihappy").iterdir():
            text = file.read_text()
            url = f"https://www.rihappy.com.br/{file.stem}/p"
            items = parser.parse(text=text, url=url, marketplace="rihappy")

            for item in items:
                pprint(item.dict())


if __name__ == "__main__":
    unittest.main()
