import json
import re
from collections.abc import Generator

import pyjson5
from babel.numbers import parse_decimal
from la_deep_get import dget
from page_models import SKU, URL, Attribute, Image, Metadata, Price, Rating, Video
from parsel import Selector, SelectorList
from structlog.stdlib import BoundLogger
from url_builder import Builder as UrlBuilder
from url_parser import Parser as UrlParser

from page_parser.abstractions import Marketplace


class Amazon(Marketplace):
    def __init__(self, marketplace: str, logger: BoundLogger) -> None:
        super().__init__(marketplace, logger)

        self._locale = "pt_BR"
        self._url_parser = UrlParser(logger=logger)
        self._url_builder = UrlBuilder(logger=logger)

    def parse(self, text: str, url: URL) -> Generator[SKU | URL, tuple[str, URL], None]:
        selector = Selector(text=text)
        scripts: list[str] = selector.xpath(
            "//script[@type='text/javascript']"
        ).getall()

        code = self._get_code(url=url)
        name = self._get_name(selector=selector)
        brand = self._get_brand(selector=selector)
        description = self._get_description(selector=selector)
        prices = self._get_prices(selector=selector)
        segments = self._get_segments(selector=selector)
        attributes = self._get_attributes(selector=selector)
        rating = self._get_rating(selector=selector)
        images = self._get_images(scripts=scripts)
        videos = self._get_videos(scripts=scripts)
        variations = self._get_variations(scripts=scripts)

        yield SKU(
            code=code,
            marketplace=self._marketplace,
            name=name,
            brand=brand,
            description=description,
            prices=prices,
            segments=segments,
            attributes=attributes,
            rating=rating,
            images=images,
            videos=videos,
            variations=variations,
            metadata=Metadata(sources=[url]),
        )

    def _get_code(self, url: URL) -> str:
        url_parsed = self._url_parser.parse(url, self._marketplace)
        return url_parsed.code

    def _get_name(self, selector: Selector) -> str:
        return selector.xpath("//span[@id='productTitle']//text()").get()

    def _get_brand(self, selector: Selector) -> str | None:
        brand: str | None = selector.xpath("//a[@id='bylineInfo']/text()").get()

        if brand:
            brand = brand.replace("Visite a loja ", "")
            brand = brand.replace("Marca: ", "")

        return brand

    def _get_description(self, selector: Selector) -> str | None:
        descriptions: list[str] = []

        description_1 = selector.xpath(
            "//div[@id='productDescription']//span/text()"
        ).get(default="")
        descriptions.append(description_1)

        description_2: list[str] = selector.xpath(
            "//div[@id='feature-bullets']//span/text()"
        ).getall()
        descriptions.extend(description_2)

        description_3: str = selector.xpath(
            "//div[@data-a-expander-name='book_description_expander']/div/span/text()"
        ).get(default="")
        descriptions.append(description_3)

        description_4: str = selector.xpath(
            "//div[@id='editorialReviews_feature_div']/div[2]//div//span/text()"
        ).get(default="")
        descriptions.append(description_4)

        description_5_div: SelectorList = selector.xpath("//div[@id='aplus']/div")
        description_5_div.xpath(".//style").remove()
        description_5_div.xpath(".//script").remove()
        description_5_div.xpath(".//a[@href='javascript:void(0)']").remove()
        description_5: list[str] = description_5_div.xpath(".//text()").getall()
        descriptions.extend(description_5)

        descriptions = [d.strip() for d in descriptions]
        descriptions = [d for d in descriptions if d]
        description = "\n".join(descriptions) or None

        return description

    def _get_prices(self, selector: Selector) -> list[Price]:
        currencies: list[str] = selector.xpath(
            "//span[@class='a-price-symbol']//text()"
        ).getall()
        currencies = [c.strip() for c in currencies]
        currencies = [c for c in currencies if c]
        currency = currencies[0] if currencies else None

        prices = []

        price_1_whole: str | None = selector.xpath(
            "//div[@id='corePrice_feature_div']//span[@class='a-price-whole']//text()"
        ).get()
        price_1_fraction: str | None = selector.xpath(
            "//span[@class='a-price-fraction']//text()"
        ).get()
        price_1_parts = [price_1_whole, price_1_fraction]
        price_1_parts = [p for p in price_1_parts if p]

        if price_1_whole:
            price_1 = ",".join(price_1_parts)
            price_1 = parse_decimal(price_1, locale=self._locale)
            price_1 = Price(installments=[price_1], currency=currency)
            prices.append(price_1)

        price_2_secondary: str | None = selector.xpath(
            "//span[@data-a-color='secondary']/span/text()"
        ).get()

        if price_2_secondary and currency:
            price_2 = price_2_secondary.replace(currency, "")
            price_2 = parse_decimal(price_2, locale=self._locale)
            price_2 = Price(installments=[price_2], currency=currency)
            prices.append(price_2)

        price_3_range: list[str] = selector.xpath(
            "//div[@id='apex_desktop']//span[contains(@class, 'apexPriceToPay')]/span[@class='a-offscreen']/text()"
        ).getall()

        for price_3 in price_3_range:
            price_3: str
            price_3 = price_3.replace(currency, "")
            price_3 = parse_decimal(price_3, locale=self._locale)
            price_3 = Price(installments=[price_3], currency=currency)
            prices.append(price_3)

        return prices

    def _get_segments(self, selector: Selector) -> list[str]:
        segments: list[str] = selector.xpath(
            "//div[contains(@class, 'a-breadcrumb')]//text()"
        ).getall()
        segments = [s.strip() for s in segments]
        segments = [s for s in segments if s]
        segments = [s for s in segments if s != "›"]

        # Quando é um resultado de busca os segmentos não aparecem,
        # em vez disso tem um "‹ Voltar aos resultados"
        if "‹" in segments:
            return []

        return segments

    def _get_attributes(self, selector: Selector) -> list[Attribute]:
        attributes = []

        attributes_1_tr = selector.xpath("//div[@id='productOverview_feature_div']//tr")
        for attribute_1_tr in attributes_1_tr:
            attribute_1_tr: SelectorList
            attributes_1_td = attribute_1_tr.xpath(".//td/span/text()").getall()
            attribute_1 = Attribute(name=attributes_1_td[0], value=attributes_1_td[1])
            attributes.append(attribute_1)

        attributes_2_tr = selector.xpath(
            "//table[@id='productDetails_techSpec_section_1']//tr"
        )
        for attribute_2_tr in attributes_2_tr:
            attribute_2_tr: SelectorList
            attributes_2_th = attribute_2_tr.xpath(".//th//text()").get()
            attributes_2_td = attribute_2_tr.xpath(".//td//text()").get()
            attribute_2 = Attribute(name=attributes_2_th, value=attributes_2_td)
            attributes.append(attribute_2)

        attributes_3_tr = selector.xpath(
            "//table[@id='productDetails_detailBullets_sections1']//tr"
        )
        for attribute_3_tr in attributes_3_tr:
            attribute_3_tr: SelectorList

            attribute_3_th = attribute_3_tr.xpath(".//th//text()").get()

            # Os valores de:
            # "Avaliações de clientes"
            # "Ranking dos mais vendidos"
            # possuem um HTML mais complicado
            # por isso pegamos todos os textos e juntamos
            attribute_3_tr.xpath(".//td//style").remove()
            attribute_3_tr.xpath(".//td//script").remove()
            attribute_3_tds: list[str] = attribute_3_tr.xpath(".//td//text()").getall()
            attribute_3_tds = [a.strip() for a in attribute_3_tds]
            attribute_3_tds = [a for a in attribute_3_tds if a]

            # Remove duplicados e mantem a ordem
            # (usando set a ordem iria embora)
            attribute_3_tds = {a: 1 for a in attribute_3_tds}.keys()
            attribute_3_td = "\n".join(attribute_3_tds)

            attribute_3 = Attribute(name=attribute_3_th, value=attribute_3_td)
            attributes.append(attribute_3)

        attributes_4_tr = selector.xpath(
            "//table[@id='technicalSpecifications_section_1']//tr"
        )
        for attribute_4_tr in attributes_4_tr:
            attribute_4_tr: SelectorList
            attribute_4_th = attribute_4_tr.xpath(".//th/text()").get()
            attribute_4_td = attribute_4_tr.xpath(".//td/text()").get()
            attribute_4 = Attribute(name=attribute_4_th, value=attribute_4_td)
            attributes.append(attribute_4)

        attributes_5_li = selector.xpath("//div[@id='detailBullets_feature_div']//li")
        for attribute_5_li in attributes_5_li:
            attribute_5_li: SelectorList
            attribute_5_span: list[str] = attribute_5_li.xpath(
                ".//span/span/text()"
            ).getall()
            attribute_5_span = [a.strip() for a in attribute_5_span]
            attribute_5_span = [a for a in attribute_5_span if a]

            if len(attribute_5_span) < 2:
                continue

            attribute_5_name: str = attribute_5_span[0]
            attribute_5_name = attribute_5_name.partition(":")[0]
            attribute_5_name = attribute_5_name.partition("\n")[0]
            attribute_5_value: str = attribute_5_span[1]
            attribute_5 = Attribute(name=attribute_5_name, value=attribute_5_value)
            attributes.append(attribute_5)

        return attributes

    def _get_rating(self, selector: Selector) -> Rating:
        rating = Rating(min=1, max=5)

        rating_span: str = selector.xpath(
            "//span[@data-hook='rating-out-of-text']/text()"
        ).get(default="")

        if " de 5" in rating_span:
            rating_span = rating_span.partition(" de 5")[0]
            rating_span = rating_span.strip()
            rating_current = parse_decimal(rating_span, locale=self._locale)
            rating.current = rating_current

        return rating

    def _get_images(self, scripts: list[str]) -> list[str]:
        images = []

        images_1_scripts = [s for s in scripts if "'colorImages': " in s]
        images_1_scripts = [s.split("'colorImages':")[1] for s in images_1_scripts]
        images_1_scripts = [s.split("'colorToAsin':")[0] for s in images_1_scripts]
        images_1_scripts = [s.strip() for s in images_1_scripts]

        for images_1_script in images_1_scripts:
            if images_1_script.endswith(","):
                images_1_script = images_1_script[:-1]

            images_1_js: dict = pyjson5.loads(images_1_script)
            images_1_ini: list[dict] = [
                i for i in dget(images_1_js, "initial", default=[])
            ]
            images_1_main: list[dict] = [i.get("main", {}) for i in images_1_ini]

            for image_1_main in images_1_main:
                for image_1_url in image_1_main:
                    # The url last number is the size and it's customizable
                    image_1_url = re.sub(r"[0-9]+_\.jpg", "9999_.jpg", image_1_url)
                    images.append(Image(url=image_1_url))

                    break  # No need to get all sizes from same image

        images_2_scripts = [s for s in scripts if "'imageGalleryData'" in s]
        images_2_scripts = [
            s.split("'imageGalleryData' :")[1] for s in images_2_scripts
        ]
        images_2_scripts = [s.split("'centerColMargin'")[0] for s in images_2_scripts]
        images_2_scripts = [s.strip() for s in images_2_scripts]

        for images_2_script in images_2_scripts:
            if images_2_script.endswith(","):
                images_2_script = images_2_script[:-1]

            images_2_json: list[dict] = pyjson5.loads(images_2_script)
            images_2_json = [i.get("mainUrl") for i in images_2_json]
            images_2_json = [i for i in images_2_json if i]

            for image_2_url in images_2_json:
                images.append(Image(url=image_2_url))

        return images

    def _get_videos(self, scripts: list[str]) -> list[str]:
        videos = []

        videos_scripts = [s for s in scripts if "jQuery.parseJSON('{\"dataInJson" in s]
        videos_scripts = [s.split("jQuery.parseJSON('")[1] for s in videos_scripts]
        videos_scripts = [
            s.split('data["alwaysIncludeVideo"]')[0] for s in videos_scripts
        ]
        videos_scripts = [s.strip() for s in videos_scripts]

        for videos_script in videos_scripts:
            if videos_script.endswith("');"):
                videos_script = videos_script[:-3]

            videos_json: dict = json.loads(videos_script)
            videos_list: list[dict] = videos_json.get("videos", [])
            videos_urls = [v.get("url") for v in videos_list]
            videos_urls = [v for v in videos_urls if v]

            for video_url in videos_urls:
                videos.append(Video(url=video_url))

        return videos

    def _get_variations(self, scripts: list[str]) -> list[str]:
        variations = []

        variations_1_scripts = [
            s for s in scripts if "jQuery.parseJSON('{\"dataInJson" in s
        ]
        variations_1_scripts = [
            s.split("jQuery.parseJSON('")[1] for s in variations_1_scripts
        ]
        variations_1_scripts = [
            s.split('data["alwaysIncludeVideo"]')[0] for s in variations_1_scripts
        ]
        variations_1_scripts = [s.strip() for s in variations_1_scripts]

        for variations_1_script in variations_1_scripts:
            if variations_1_script.endswith("');"):
                variations_1_script = variations_1_script[:-3]

            variations_1_json: dict = json.loads(variations_1_script)
            variations_1_colors: dict = dget(
                variations_1_json, "colorToAsin", default={}
            )
            variations_1_asins: list[dict] = [v for v in variations_1_colors.values()]

            for variations_1_asin in variations_1_asins:
                variation_1_asin = variations_1_asin.get("asin")

                if variation_1_asin:
                    variations.append(
                        self._url_builder.build_sku_url(
                            variation_1_asin,
                            self._marketplace,
                        )
                    )

        variations_2_scripts = [s for s in scripts if "var dataToReturn =" in s]
        variations_2_scripts = [
            s.split("var dataToReturn =")[1] for s in variations_2_scripts
        ]
        variations_2_scripts = [
            s.split("return dataToReturn;")[0] for s in variations_2_scripts
        ]
        variations_2_scripts = [s.strip() for s in variations_2_scripts]

        for variations_2_script in variations_2_scripts:
            if variations_2_script.endswith(";"):
                variations_2_script = variations_2_script[:-1]
            variations_2_js: dict = pyjson5.loads(variations_2_script)
            variations_2_js: dict = variations_2_js.get("dimensionToAsinMap", {})
            variations_2_asins = [v for v in variations_2_js.values()]

            for variations_2_asin in variations_2_asins:
                variations.append(
                    self._url_builder.build_sku_url(
                        variations_2_asin,
                        self._marketplace,
                    )
                )

        return variations
