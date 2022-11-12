import unittest
from collections.abc import Generator
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_models import SKU, URL
from url_builder import Builder

from page_parser.parser import Parser


class TestAmazon(TestCase):
    def setUp(self) -> None:
        self._parser = Parser()
        self._builder = Builder()
        self._marketplace = "amazon"
        self._dir = f"tests/res/{self._marketplace}"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(self._dir).iterdir():
            if file.is_dir():
                self._parse_directory(file)
            else:
                self._parse_file(file)

    def _parse_file(self, file: Path) -> None:
        text = file.read_text()
        url = self._builder.build_sku_url(file.stem, self._marketplace)
        skus = self._parser.parse_sku(text=text, url=url, marketplace=self._marketplace)

        for sku in skus:
            pprint(sku.dict())

    def _parse_directory(self, directory: Path) -> None:
        url = self._builder.build_sku_url(directory.name, self._marketplace)
        files = sorted(directory.iterdir())
        generator: Generator[SKU | URL, tuple[str, URL], None] = None

        for file in files:
            if not generator:
                generator = self._parser.parse_sku(
                    text=file.read_text(), url=url, marketplace=self._marketplace
                )
                item = generator.send(None)
            else:
                item = generator.send(file.read_text())

            if isinstance(item, SKU):
                pprint(item.dict())


if __name__ == "__main__":
    unittest.main()
