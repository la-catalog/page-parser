import json
import re
from collections.abc import Generator

from babel.numbers import parse_decimal
from la_deep_get import dget
from page_sku import SKU, Attribute
from parsel import Selector, SelectorList

from page_parser.abstractions import Marketplace


class Rihappy(Marketplace):
    """
    Base class for the marketplaces classes.
    """

    def __init__(self, logger) -> None:
        self._logger = logger

    def parse(self, text: str, url: str) -> Generator[list[SKU], tuple[str, str], None]:
        selector = Selector(text=text)

        product = selector.xpath(
            "//template[@data-varname='__STATE__']/script/text()"
        ).get()
        product = json.loads(product) if product else None

        name = selector.xpath(
            "//h1[contains(@class, 'vtex-store-components-3-x-productNameContainer')]//text()"
        ).get()

        code = selector.xpath(
            "//span[@class='vtex-product-identifier-0-x-product-identifier__value']/text()"
        ).get()

        price_1 = selector.xpath(
            "(//span[contains(@class, 'vtex-product-price-1-x-currencyContainer')])[1]//text()"
        ).getall()
        price_1 = "".join(price_1)
        price_1 = re.sub(r"[^0-9,]", "", price_1)
        price_1 = parse_decimal(price_1, locale="pt_BR") if price_1 else None

        price_2 = selector.xpath(
            "(//span[contains(@class, 'vtex-product-price-1-x-currencyContainer')])[3]//text()"
        ).getall()
        price_2 = "".join(price_2)
        price_2 = re.sub(r"[^0-9,]", "", price_2)
        price_2 = parse_decimal(price_2, locale="pt_BR") if price_2 else None

        currency = selector.xpath(
            "//span[contains(@class, 'vtex-product-price-1-x-currencyCode')]/text()"
        ).get()

        print(description)

        attributes: list[Selector] = selector.xpath(
            "//div[contains(@class, 'vtex-flex-layout-0-x-flexRow--product-specification-value')]"
        ).getall()

        print(attributes)

        attributes = [
            Attribute(
                name=attribute.xpath(".//div/div[1]/text()"),
                value=attribute.xpath(".//div/div[2]/text()"),
            )
            for attribute in attributes
        ]

        print(attributes)
