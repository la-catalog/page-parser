import unittest
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_parser.parser import Parser


class TestAmazon(TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.marketplace = "amazon"
        self.url = "https://www.amazon.com.br/dp/{0}"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(f"tests/{self.marketplace}").iterdir():
            text = file.read_text()
            url = self.url.format(file.stem)
            items = self.parser.parse(text=text, url=url, marketplace=self.marketplace)

            for item in items:
                pprint(item.dict())
        print()

    def test_parse_1(self) -> None:
        filename = "8565042472.html"
        file = Path(f"tests/{self.marketplace}/{filename}")
        text = file.read_text()
        url = self.url.format(file.stem)
        items = self.parser.parse(text=text, url=url, marketplace=self.marketplace)

        for item in items:
            pprint(item.dict())
        print()


if __name__ == "__main__":
    unittest.main()
