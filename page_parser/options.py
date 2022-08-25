from structlog.stdlib import BoundLogger

from page_parser import marketplace_sku
from page_parser.abstractions import Marketplace
from page_parser.exceptions import UnknowMarketplaceError
from page_parser.marketplace_search.rihappy import Rihappy as SearchRihappy
from page_parser.marketplace_sku.amazon import Amazon as SKUAmazon
from page_parser.marketplace_sku.amazon_pt import AmazonPT as SKUAmazonPT
from page_parser.marketplace_sku.mercado_livre_api import (
    MercadoLivreAPI as SKUMercadoLivreAPI,
)
from page_parser.marketplace_sku.rihappy import Rihappy as SKURihappy

search_options: dict[str, type[Marketplace]] = {
    "rihappy": SearchRihappy,
}

sku_options: dict[str, type[Marketplace]] = {
    "rihappy": SKURihappy,
    "amazon": SKUAmazon,
    "amazon_pt": SKUAmazonPT,
    "mercado_livre": SKUMercadoLivreAPI,
}


def get_marketplace_sku_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    try:
        new_logger = logger.bind(marketplace=marketplace)
        marketplace_class = sku_options[marketplace]
        return marketplace_class(marketplace=marketplace, logger=new_logger)
    except KeyError as e:
        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package"
        ) from e


def get_marketplace_search_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    try:
        new_logger = logger.bind(marketplace=marketplace)
        marketplace_class = sku_options[marketplace]
        return marketplace_class(marketplace=marketplace, logger=new_logger)
    except KeyError as e:
        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package"
        ) from e
