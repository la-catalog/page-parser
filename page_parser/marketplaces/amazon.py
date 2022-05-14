import json
import re
from collections.abc import Generator

import pyjson5
from babel.numbers import parse_decimal
from la_deep_get import dget
from page_sku import SKU, Attribute, Price
from parsel import Selector, SelectorList
from pydantic import AnyHttpUrl
from url_parser import Parser as UrlParser
from url_parser import SkuUrl

from page_parser.abstractions import Marketplace


class Amazon(Marketplace):
    def parse(
        self, text: str, url: AnyHttpUrl
    ) -> Generator[SKU | AnyHttpUrl, tuple[str, AnyHttpUrl], None]:
        url_parser = UrlParser(self._logger)
        selector = Selector(text=text)

        url_parsed = url_parser.parse(url, self._marketplace)
        code = url_parsed.code
        name = selector.xpath("//span[@id='productTitle']//text()").get()

        ###### BRAND

        brand: str = selector.xpath("//a[@id='bylineInfo']/text()").get(default="")
        brand = brand.replace("Visite a loja ", "")
        brand = brand.replace("Marca: ", "")

        ###### DESCRIPTION

        description_1 = selector.xpath(
            "//div[@id='productDescription']//span/text()"
        ).get(default="")

        description_2_bullets: list[str] = selector.xpath(
            "//div[@id='feature-bullets']//span/text()"
        ).getall()
        description_2_bullets = [d.strip() for d in description_2_bullets]
        description_2_bullets = [d for d in description_2_bullets if d]
        description_2 = "\n".join(description_2_bullets)

        description = "\n".join([description_1, description_2])

        ###### PRICE

        currencies: list[str] = selector.xpath(
            "//span[@class='a-price-symbol']//text()"
        ).getall()
        currencies = [c.strip() for c in currencies]
        currencies = [c for c in currencies if c]
        currency = currencies[0] if currencies else None

        prices = []

        price_1_whole = selector.xpath(
            "//div[@id='corePrice_feature_div']//span[@class='a-price-whole']//text()"
        ).get()
        price_1_fraction = selector.xpath(
            "//span[@class='a-price-fraction']//text()"
        ).get()
        price_1_parts = [price_1_whole, price_1_fraction]
        price_1_parts = [p for p in price_1_parts if p]

        if price_1_whole and price_1_parts:
            price_1 = ",".join(price_1_parts)
            price_1 = parse_decimal(price_1, locale="pt_BR")
            price_1 = Price(amount=price_1, currency=currency)
            prices.append(price_1)

        price_2_secondary = selector.xpath(
            "//span[@data-a-color='secondary']/span/text()"
        ).get()

        if price_2_secondary and currency:
            price_2 = price_2_secondary.replace(currency, "")
            price_2 = parse_decimal(price_2, locale="pt_BR")
            price_2 = Price(amount=price_2, currency=currency)
            prices.append(price_2)

        price_3_range = selector.xpath(
            "//div[@id='apex_desktop']//span[contains(@class, 'apexPriceToPay')]/span[@class='a-offscreen']/text()"
        ).getall()

        for price_3 in price_3_range:
            price_3: str
            price_3 = price_3.replace(currency, "")
            price_3 = parse_decimal(price_3, locale="pt_BR")
            price_3 = Price(amount=price_3, currency=currency)
            prices.append(price_3)

        ###### SEGMENTS

        segments: list[str] = selector.xpath(
            "//div[contains(@class, 'a-breadcrumb')]//text()"
        ).getall()
        segments = [s.strip() for s in segments]
        segments = [s for s in segments if s]
        segments = [s for s in segments if s != "›"]

        # Quando é um resultado de busca os segmentos não aparecem,
        # em vez disso tem um "‹ Voltar aos resultados"
        if "‹" in segments:
            segments = []

        ###### ATTRIBUTES

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
            attribute_5_span = attribute_5_li.xpath(".//span/span/text()").getall()
            attribute_5_name: str = attribute_5_span[0]
            attribute_5_name = attribute_5_name.partition(":")[0]
            attribute_5_name = attribute_5_name.partition("\n")[0]
            attribute_5_value: str = attribute_5_span[1]
            attribute_5 = Attribute(name=attribute_5_name, value=attribute_5_value)
            attributes.append(attribute_5)

        ###### IMAGES

        images = []

        scripts: list[str] = selector.xpath(
            "//script[@type='text/javascript']"
        ).getall()
        images_scripts = [s for s in scripts if "'colorImages': " in s]
        images_scripts = [s.split("'colorImages':")[1] for s in images_scripts]
        images_scripts = [s.split("'colorToAsin':")[0] for s in images_scripts]
        images_scripts = [s.strip() for s in images_scripts]

        for images_script in images_scripts:
            if images_script[-1] == ",":
                images_script = images_script[:-1]

            images_js: dict = pyjson5.loads(images_script)
            images_ini: list[dict] = [i for i in dget(images_js, "initial", default=[])]
            images_main: list[dict] = [i.get("main", {}) for i in images_ini]

            for image_main in images_main:
                for image_url in image_main:
                    image_url = re.sub(r"[0-9]+_\.jpg", "9999_.jpg", image_url)
                    images.append(image_url)
                    break  # no need to get all sizes from same image

        ###### VIDEOS

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
                videos.append(video_url)

        ###### VARIATIONS

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
                        f"https://www.amazon.com.br/dp/{variation_1_asin}"
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
                variations.append(f"https://www.amazon.com.br/dp/{variations_2_asin}")

        yield SKU(
            code=code,
            name=name,
            brand=brand,
            description=description,
            prices=prices,
            segments=segments,
            attributes=attributes,
            images=images,
            videos=videos,
            variations=variations,
            sources=[url],
            marketplace=self._marketplace,
        )
