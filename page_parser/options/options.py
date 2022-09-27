from structlog.stdlib import BoundLogger

from page_parser.abstractions import Marketplace
from page_parser.exceptions import UnknowMarketplaceError
from page_parser.options.search_options import search_options
from page_parser.options.sku_options import sku_options


def get_marketplace_parser(
    marketplace: str, options: dict[str, type[Marketplace]], logger: BoundLogger
) -> Marketplace:
    """
    Get a parser responsible for a marketplace.

    Each marketplace can have many type of pages (sku page, search page, home page, etc)
    and all values in `options` should be a parser from the same type of page.

    marketplace - String that represents the marketplace
    options - Dictionary with parsers for one type of page
    logger - A logger to be attached to parser
    """

    try:
        new_logger = logger.bind(marketplace=marketplace)
        marketplace_class = options[marketplace]
        return marketplace_class(marketplace=marketplace, logger=new_logger)
    except KeyError as e:
        valid = ", ".join(options.keys())

        raise UnknowMarketplaceError(
            f"Marketplace '{marketplace}' is not defined in page_parser package. Valid options: {valid}"
        ) from e


def get_sku_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    """
    Get a SKU parser responsible for a marketplace.

    Is a shortcut for calling `get_marketplace_parser`
    when you want a SKU parser.
    """

    return get_marketplace_parser(
        marketplace=marketplace, options=sku_options, logger=logger
    )


def get_search_parser(marketplace: str, logger: BoundLogger) -> Marketplace:
    """
    Get a search parser responsible for a marketplace.

    Is a shortcut for calling `get_marketplace_parser`
    when you want a search parser.
    """

    return get_marketplace_parser(
        marketplace=marketplace, options=search_options, logger=logger
    )
