import json
from collections.abc import Generator

from la_deep_get import dget
from page_models import SKU, Attribute, Price
from parsel import Selector
from pydantic import AnyHttpUrl

from page_parser.abstractions import Marketplace


class Rihappy(Marketplace):
    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        selector = Selector(text=text)
