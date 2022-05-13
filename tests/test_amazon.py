import unittest
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_parser.parser import Parser


class TestAmazon(TestCase):
    def test_parse(self) -> None:
        parser = Parser()

        for file in Path("tests/amazon").iterdir():
            text = file.read_text()
            url = f"https://www.amazon.com.br/dp/{file.stem}"
            items = parser.parse(text=text, url=url, marketplace="amazon")

            for item in items:
                pprint(item.dict())


if __name__ == "__main__":
    unittest.main()
