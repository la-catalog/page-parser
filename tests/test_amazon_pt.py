import unittest
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_parser.parser import Parser


class TestAmazon(TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.marketplace = "amazon_pt"
        self.url = "https://www.amazon.es/-/pt/dp/{0}"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(f"tests/{self.marketplace}").iterdir():
            text = file.read_text()
            url = self.url.format(file.stem)
            items = self.parser.parse_sku(
                text=text, url=url, marketplace=self.marketplace
            )

            for item in items:
                pprint(item.dict())
        print()


if __name__ == "__main__":
    unittest.main()
