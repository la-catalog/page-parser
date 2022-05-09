import json
import re
from collections.abc import Generator

from babel.numbers import parse_decimal
from la_deep_get import dget
from page_sku import SKU, Attribute, Price
from parsel import Selector, SelectorList
from url_parser import Parser as UrlParser

from page_parser.abstractions import Marketplace


class Rihappy(Marketplace):
    """
    Base class for the marketplaces classes.
    """

    def __init__(self, logger) -> None:
        self._logger = logger
        self._url_parser = UrlParser(logger)

    def parse(self, text: str, url: str) -> Generator[list[SKU], tuple[str, str], None]:
        selector = Selector(text=text)

        json_ = selector.xpath(
            "//template[@data-varname='__STATE__']/script/text()"
        ).get("{}")
        json_: dict = json.loads(json_)
        product = dget(list(json_.keys()), 0)
        product = json_.get(product, {})

        name = product.get("productName")
        code = product.get("productId")
        brand = product.get("brand")
        description = product.get("description")

        segments: list[str] = dget(product, "categories", "json") or []
        segments: str = dget(segments, 0, default="")
        segments: list[str] = segments.split("/")
        segments = [segment for segment in segments if segment]

        currency = selector.xpath(
            "//span[contains(@class, 'vtex-product-price-1-x-currencyCode')]/text()"
        ).get("R$")

        prices: str = dget(product, "priceRange", "id")
        prices: dict = json_.get(prices, {})
        prices: list[str] = [dget(value, "id") for value in prices.values()]
        prices_high: list[float] = [dget(json_, id_, "highPrice") for id_ in prices]
        prices_low: list[float] = [dget(json_, id_, "lowPrice") for id_ in prices]
        prices: set[str] = set(prices_high + prices_low)
        prices: set[str] = set(price for price in prices if price)
        prices: list[Price] = [
            Price(amount=price, currency=currency) for price in prices
        ]

        attributes: list = dget(product, "specificationGroups", default=[])
        attributes: str = dget(attributes, -1, "id")
        attributes: list[dict] = dget(json_, attributes, "specifications", default=[])
        attributes: list[str] = [attribute.get("id") for attribute in attributes]
        attributes: list[dict] = [json_.get(attribute) for attribute in attributes]
        attributes: list[Attribute] = [
            Attribute(
                name=attribute.get("name"),
                value=". ".join(dget(attribute, "values", "json", default=[])),
            )
            for attribute in attributes
        ]

        print(name)
        print(code)
        print(brand)
        print(description)
        print(segments)
        print(currency)
        print(prices)
        print(attributes)
