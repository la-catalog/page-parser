import json
from collections.abc import Generator

from la_deep_get import dget
from page_models import SKU, URL, Attribute, Price
from page_models.sku.metadata import Metadata
from parsel import Selector

from page_parser.abstractions import Marketplace


class Rihappy(Marketplace):
    def parse(self, text: str, url: URL) -> Generator[SKU | URL, tuple[str, URL], None]:
        selector = Selector(text=text)

        json_ = selector.xpath(
            "//template[@data-varname='__STATE__']/script/text()"
        ).get("{}")
        json_: dict = json.loads(json_)
        first_key = next(iter(json_), {})
        product = json_.get(first_key, {})

        code = product.get("productId")
        name = product.get("productName")
        brand = product.get("brand")
        description = product.get("description")

        ###### SEGMENTS

        segments = dget(product, "categories", "json") or []
        segments_together: str = dget(segments, 0, default="")
        segments = segments_together.split("/")
        segments = [s for s in segments if s]

        ###### PRICES

        currency = selector.xpath(
            "//span[contains(@class, 'vtex-product-price-1-x-currencyCode')]/text()"
        ).get("R$")

        prices: str = dget(product, "priceRange", "id")
        prices: dict = json_.get(prices, {})
        prices: list[str] = [dget(v, "id") for v in prices.values()]
        prices_high: list[float] = [dget(json_, id_, "highPrice") for id_ in prices]
        prices_low: list[float] = [dget(json_, id_, "lowPrice") for id_ in prices]
        prices: set[str] = set(prices_high + prices_low)
        prices: set[str] = set(p for p in prices if p)
        prices: list[Price] = [Price(amount=p, currency=currency) for p in prices]

        ###### ATTRIBUTES

        attributes: list = dget(product, "specificationGroups", default=[])
        attributes: str = dget(attributes, -1, "id")
        attributes: list[dict] = dget(json_, attributes, "specifications", default=[])
        attributes: list[str] = [a.get("id") for a in attributes]
        attributes: list[dict] = [json_.get(a) for a in attributes]
        attributes: list[Attribute] = [
            Attribute(
                name=a.get("name"),
                value=". ".join(dget(a, "values", "json", default=[])),
            )
            for a in attributes
        ]

        ###### IMAGES

        images_first_item = dget(product, "items", 0, "id")
        images_item: list[dict] = dget(json_, images_first_item, "images", default=[])
        images_ids = [i.get("id") for i in images_item]
        images = [dget(json_, i, "imageUrl") for i in images_ids]

        yield SKU(
            code=code,
            marketplace=self._marketplace,
            name=name,
            brand=brand,
            description=description,
            prices=prices,
            segments=segments,
            attributes=attributes,
            images=images,
            metadata=Metadata(sources=[url]),
        )
