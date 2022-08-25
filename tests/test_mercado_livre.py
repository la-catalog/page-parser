import unittest
from collections.abc import Generator
from pathlib import Path
from pprint import pprint
from unittest import TestCase

from page_models import SKU, AnURL

from page_parser.parser import Parser


class TestRihappy(TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.marketplace = "mercado_livre"
        self.url = "https://api.mercadolibre.com/items/{0}"

        return super().setUp()

    def test_parse(self) -> None:
        for file in Path(f"tests/{self.marketplace}").iterdir():
            if file.is_dir():
                self._parse_directory(file)
            else:
                self._parse_file(file)

    def _parse_file(self, file: Path) -> None:
        text = file.read_text()
        url = self.url.format(file.stem)
        generator = self.parser.parse_sku(
            text=text, url=url, marketplace=self.marketplace
        )

        for item in generator:
            pprint(item.dict())

    def _parse_directory(self, directory: Path) -> None:
        url = self.url.format(directory.name)
        files = sorted(directory.iterdir())
        generator: Generator[SKU | AnURL, tuple[str, AnURL], None] = None

        for file in files:
            text = file.read_text()

            if not generator:
                generator = self.parser.parse_sku(
                    text=text, url=url, marketplace=self.marketplace
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
