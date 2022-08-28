import json
from collections.abc import Generator

from babel.numbers import parse_decimal
from la_deep_get import dget
from page_models import SKU, AnURL, Attribute, Measurement, Price
from page_models.sku.metadata import Metadata
from pydantic import AnyHttpUrl
from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace


class MercadoLivreAPI(Marketplace):
    def __init__(self, marketplace: str, logger: BoundLogger) -> None:
        super().__init__(marketplace, logger)

        self._description_endpoint = (
            "https://api.mercadolibre.com/items/{0}/description"
        )
        self._currency_endpoint = "https://api.mercadolibre.com/currencies/{0}"
        self._category_endpoint = "https://api.mercadolibre.com/categories/{0}"
        self._picture_endpoint = "https://api.mercadolibre.com/pictures/{0}"

    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        json_: dict = json.loads(text)

        code = json_.get("id")
        name = json_.get("title")
        description = yield from self._get_description(json_)
        prices = yield from self._get_prices(json_)
        segments = yield from self._get_segments(json_)
        attributes = self._get_attributes(json_)
        package = self._get_package(json_)
        images = yield from self._get_images(json_)

        yield SKU(
            code=code,
            marketplace=self._marketplace,
            name=name,
            description=description,
            prices=prices,
            segments=segments,
            attributes=attributes,
            package=package,
            images=images,
            metadata=Metadata(sources=[url]),
        )

    def _get_description(self, json_: dict) -> Generator[AnURL, str, str]:
        description = None

        description_url = self._description_endpoint.format(json_["id"])
        description_text = yield AnURL(url=description_url)

        if description_text:
            description_json: dict = json.loads(description_text)
            description = description_json.get("plain_text")

        return description

    def _get_prices(self, json_: dict) -> Generator[AnURL, str, list[Price]]:
        prices = []

        if currency_id := json_.get("currency_id"):
            currency_url = self._currency_endpoint.format(currency_id)
            currency_text = yield AnURL(url=currency_url)

            if currency_text:
                currency_json: dict = json.loads(currency_text)
                currency = currency_json.get("symbol")
                price_1 = json_.get("price")
                price_2 = json_.get("base_price")

                if price_1:
                    prices.append(Price(amount=price_1, currency=currency))

                if price_2:
                    prices.append(Price(amount=price_2, currency=currency))

        return prices

    def _get_segments(self, json_: dict) -> Generator[AnURL, str, list[str]]:
        segments = []

        if category_id := json_.get("category_id"):
            category_url = self._category_endpoint.format(category_id)
            category_text = yield AnURL(url=category_url)

            if category_text:
                category_json: dict = json.loads(category_text)

                for category_path in category_json.get("path_from_root", []):
                    segments.append(category_path.get("name"))

        segments = [s for s in segments if s]

        return segments

    def _get_attributes(self, json_: dict) -> list[Attribute]:
        attributes = []

        for attribute in json_.get("attributes"):
            attribute: dict
            attribute_name = attribute.get("name")
            attribute_value = attribute.get("value_name")
            attributes.append(Attribute(name=attribute_name, value=attribute_value))

        return attributes

    def _get_package(self, json_: dict) -> Measurement:
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

        return package

    def _get_images(self, json_: dict) -> Generator[AnURL, str, list[str]]:
        images = []

        for picture in json_.get("pictures", []):
            picture_url = self._picture_endpoint.format(picture["id"])
            picture_text = yield AnURL(url=picture_url)

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

        return images
