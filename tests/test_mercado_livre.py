import unittest
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.marketplace = "rihappy"
        self.url = "https://api.mercadolibre.com/items/{0}"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(f"tests/{self.marketplace}").iterdir():
            text = file.read_text()
            url = self.url.format(file.stem)
            items = self.parser.parse(text=text, url=url, marketplace=self.marketplace)

            for item in items:
                pprint(item.dict())

    def test_parse_one(self) -> None:
        filename = "MLB1197244979.html"
        file = Path(f"tests/{self.marketplace}/{filename}")
        text = file.read_text()
        url = self.url.format(file.stem)
        items = self.parser.parse(text=text, url=url, marketplace=self.marketplace)

        for item in items:
            pprint(item.dict())
        print()


if __name__ == "__main__":
    unittest.main()