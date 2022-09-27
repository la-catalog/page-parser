from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace
from page_parser.exceptions import UnknowMarketplaceError
from page_parser.options.search_options import search_options
from page_parser.options.sku_options import sku_options


def get_marketplace_parser(
    marketplace: str, options: dict[str, type[Marketplace]], logger: BoundLogger
) -> Marketplace:
    try:
        new_logger = logger.bind(marketplace=marketplace)
        marketplace_class = options[marketplace]
        return marketplace_class(marketplace=marketplace, logger=new_logger)
    except KeyError as e:
        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package"
        ) from e


def get_sku_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    return get_marketplace_parser(
        marketplace=marketplace, options=sku_options, logger=logger
    )


def get_search_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    return get_marketplace_parser(
        marketplace=marketplace, options=search_options, logger=logger
    )
