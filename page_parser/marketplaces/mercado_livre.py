import json
from collections.abc import Generator

from babel.numbers import parse_decimal
from la_deep_get import dget
from page_sku import SKU, Attribute, Measurement, Price
from parsel import Selector
from pydantic import AnyHttpUrl

from page_parser.abstractions import Marketplace


class MercadoLivre(Marketplace):
    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        json_: dict = json.loads(text)

        name = json_.get("title")

        ###### PRICE

        prices = []

        if currency_id := json_.get("currency_id"):
            currency_url = "https://api.mercadolibre.com/currencies/{0}"
            currency_url = currency_url.format(currency_id)
            currency_text = yield AnyHttpUrl(url=currency_url)

            if currency_text:
                currency_json: dict = json.loads(currency_text)
                currency = currency_json.get("symbol")
                price_1 = json_.get("price")
                price_2 = json_.get("base_price")

                if price_1:
                    prices.append(Price(amount=price_1, currency=currency))

                if price_2:
                    prices.append(Price(amount=price_2, currency=currency))

        ###### ATTRIBUTES

        attributes = []

        for attribute in json_.get("attributes"):
            attribute: dict
            attribute_name = attribute.get("name")
            attribute_value = attribute.get("value_name")
            attributes.append(Attribute(name=attribute_name, value=attribute_value))

        ###### PACKAGE

        package = Measurement()
        package_dimensions: str = dget(json_, "shipping", "dimensions")

        if package_dimensions:
            # Example: "5x9x17,349"
            # https://api.mercadolibre.com/items/MLB2644371778

            package_sizes, _, package_weight = package_dimensions.partition(",")
            package_LWH = package_sizes.split("x")

            if package_weight:
                package.weight = parse_decimal(package_weight)

            if package_length := dget(package_LWH, 0):
                package.length = parse_decimal(package_length)

            if package_width := dget(package_LWH, 1):
                package.width = parse_decimal(package_width)

            if package_height := dget(package_LWH, 2):
                package.height = parse_decimal(package_height)
