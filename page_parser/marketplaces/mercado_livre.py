import json
from collections.abc import Generator

from babel.numbers import parse_decimal
from la_deep_get import dget
from page_models import SKU, Attribute, Measurement, Price
from pydantic import AnyHttpUrl

from page_parser.abstractions import Marketplace


class MercadoLivre(Marketplace):
    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        json_: dict = json.loads(text)

        name = json_.get("title")

        ###### DESCRIPTION

        description = None

        description_endpoint = "https://api.mercadolibre.com/items/{0}/description"
        description_url = description_endpoint.format(json_["id"])
        description_text = yield AnyHttpUrl(description_url)

        if description_text:
            description_json: dict = json.loads(description_text)
            description = description_json.get("plain_text")

        ###### PRICES

        prices = []

        if currency_id := json_.get("currency_id"):
            currency_endpoint = "https://api.mercadolibre.com/currencies/{0}"
            currency_url = currency_endpoint.format(currency_id)
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

        ###### SEGMENTS

        segments = []

        if category_id := json_.get("category_id"):
            category_endpoint = "https://api.mercadolibre.com/categories/{0}"
            category_url = category_endpoint.format(category_id)
            category_text = yield AnyHttpUrl(category_url)

            if category_text:
                category_json: dict = json.loads(category_text)

                for category_path in category_json.get("path_from_root", []):
                    segments.append(category_path.get("name"))

        segments = [s for s in segments if s]

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

        ###### IMAGES

        images = []
        picture_endpoint = "https://api.mercadolibre.com/pictures/{0}"

        for picture in json_.get("pictures", default=[]):
            picture_url = picture_endpoint.format(picture["id"])
            picture_text = yield AnyHttpUrl(picture_url)

            if picture_text:
                picture_json: dict = json.loads(picture_text)
                picture_biggest: str = picture_json.get("max_size")
                picture_variations: list = picture_json.get("variations", [])

                for picture_variation in picture_variations:
                    picture_variation: dict[str, str]

                    if picture_variation.get("size") == picture_biggest:
                        images.append(picture_variation.get("url"))
                        break

        images = [i for i in images if i]

        yield SKU(
            name=name,
            description=description,
            attributes=attributes,
            prices=prices,
            segments=segments,
            attributes=attributes,
            package=package,
            images=images,
        )
