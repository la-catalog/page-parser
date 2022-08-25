import unittest
from collections.abc import Generator
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_models import SKU, AnURL
from url_builder import Builder

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def setUp(self) -> None:
        self._parser = Parser()
        self._builder = Builder()
        self._marketplace = "mercado_livre_api"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(f"tests/{self._marketplace}").iterdir():
            if file.is_dir():
                self._parse_directory(file)
            else:
                self._parse_file(file)

    def _parse_file(self, file: Path) -> None:
        text = file.read_text()
        url = self._builder.build_sku_url(file.stem, self._marketplace)
        generator = self._parser.parse_sku(
            text=text, url=url, marketplace=self._marketplace
        )

        for item in generator:
            pprint(item.dict())

    def _parse_directory(self, directory: Path) -> None:
        url = self._builder.build_sku_url(directory.name, self._marketplace)
        files = sorted(directory.iterdir())
        generator: Generator[SKU | AnURL, tuple[str, AnURL], None] = None

        for file in files:
            text = file.read_text()

            if not generator:
                generator = self._parser.parse_sku(
                    text=text, url=url, marketplace=self._marketplace
                )
                item = generator.send(None)
            else:
                item = generator.send(text)

            if isinstance(item, SKU):
                pprint(item.dict())
            elif isinstance(item, AnURL):
                url = item.url


if __name__ == "__main__":
    unittest.main()
